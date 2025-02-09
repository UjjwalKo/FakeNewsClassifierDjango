import os
import time
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from dotenv import load_dotenv
from django.http import JsonResponse
from .models import PDFDocument, ChatHistory
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai._common import GoogleGenerativeAIError

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf.file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks, user_id):
    max_retries = 5
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
            vector_store.save_local(f"{settings.MEDIA_ROOT}/faiss_indexes/user_{user_id}")
            return
        except GoogleGenerativeAIError as e:
            if "RATE_LIMIT_EXCEEDED" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer
    Context:
    {context}?

    Question: 
    {question}

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

@login_required
def pdf_chat(request):
    if request.method == 'POST':
        if 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            pdf_doc = PDFDocument.objects.create(user=request.user, file=pdf_file)
            
            pdf_docs = [pdf_doc]
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            
            try:
                get_vector_store(text_chunks, request.user.id)
                return JsonResponse({'status': 'success', 'message': 'PDF processed successfully'})
            except GoogleGenerativeAIError as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=429)
        
        elif 'question' in request.POST:
            user_question = request.POST['question']
            
            try:
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
                new_db = FAISS.load_local(f"{settings.MEDIA_ROOT}/faiss_indexes/user_{request.user.id}", embeddings, allow_dangerous_deserialization=True)
                docs = new_db.similarity_search(user_question)
                
                chain = get_conversational_chain()
                
                response = chain(
                    {"input_documents": docs, "question": user_question},
                    return_only_outputs=True
                )
                answer = response["output_text"]
                ChatHistory.objects.create(user=request.user, question=user_question, answer=answer)
                
                return JsonResponse({'status': 'success', 'answer': answer})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'pdf_chat/chat.html', {'chat_history': chat_history})