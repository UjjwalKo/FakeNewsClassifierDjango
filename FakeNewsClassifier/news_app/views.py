import requests
import os
from dotenv import load_dotenv
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError 
from django.db.models import Q
import numpy as np
from .models import Article

load_dotenv()
def fetch_news(endpoint, params):
    """
    Fetch news articles from the NewsAPI.
    """
    api_key = os.getenv("NEWS_API_KEY")
    base_url = 'https://newsapi.org/v2/'
    params['apiKey'] = api_key
    response = requests.get(base_url + endpoint, params=params)
    return response.json()

def store_articles(articles):
    """
    Store fetched articles in the database, avoiding duplicates.
    """
    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        if not title and not description:
            continue
        url = article.get('url', '')
        published_at = parse_datetime(article.get('publishedAt'))
        
        try:
            existing_article = Article.objects.filter(Q(url=url) | Q(title=title)).first()
            
            if existing_article:
                # Update the existing article if needed
                existing_article.description = description
                existing_article.url_to_image = article.get('urlToImage')
                existing_article.published_at = published_at
                existing_article.source_name = article.get('source', {}).get('name', '')
                existing_article.save()
            else:
                Article.objects.create(
                    title=title,
                    description=description,
                    url=url,
                    url_to_image=article.get('urlToImage'),
                    published_at=published_at,
                    source_name=article.get('source', {}).get('name', ''),
                    language='en'
                )
        except IntegrityError as e:
            print(f"Error storing article: {e}")
        except Exception as e:
            print(f"Unexpected error storing article: {e}")

def semantic_search(query, top_k=10):
    """
    Perform semantic search using TF-IDF and cosine similarity.
    """
    try:
        # Fetch all articles from the database
        articles = list(Article.objects.all())
        if not articles:
            return []

        # Combine title and description for each article
        documents = [f"{article.title} {article.description}" for article in articles]
        documents.append(query)

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        query_vector = tfidf_matrix[-1]  
        article_vectors = tfidf_matrix[:-1] 
        similarities = cosine_similarity(query_vector, article_vectors).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        min_similarity_threshold = 0.1  
        results = [
            (articles[idx], similarities[idx])
            for idx in top_indices
            if similarities[idx] >= min_similarity_threshold
        ]
        return results
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []

def news_search(request):
    """
    Handle search queries and display results.
    """
    query = request.GET.get('q', '')
    if query:
        search_results = semantic_search(query)
        articles = [article for article, _ in sorted(search_results, key=lambda x: x[1], reverse=True)]
    else:
        articles = []
    paginator = Paginator(articles, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/search.html', {
        'page_obj': page_obj,
        'query': query,
    })

def news_home(request):
    """
    Display the latest news articles.
    """
    news_data = fetch_news('top-headlines', {'country': 'us', 'pageSize': 100})
    articles = news_data.get('articles', [])
    try:
        store_articles(articles)
    except Exception as e:
        print(f"Error storing articles: {e}")
    paginator = Paginator(articles, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/home.html', {'page_obj': page_obj})

def news_category(request, category):
    """
    Display news articles by category.
    """
    news_data = fetch_news('top-headlines', {'country': 'us', 'category': category, 'pageSize': 100})
    articles = news_data.get('articles', [])
    try:
        store_articles(articles)
    except Exception as e:
        print(f"Error storing articles: {e}")

    paginator = Paginator(articles, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/category.html', {'page_obj': page_obj, 'category': category})

def live_news(request):
    """
    Display live news articles.
    """
    news_data = fetch_news('top-headlines', {'country': 'us', 'pageSize': 20})
    articles = news_data.get('articles', [])
    try:
        store_articles(articles)
    except Exception as e:
        print(f"Error storing articles: {e}")

    return render(request, 'news/live_news.html', {'articles': articles})