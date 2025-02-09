# Fake News Classifier

# Fake News Classifier

## Project Overview

The Fake News Classifier is a comprehensive web application designed to combat the spread of misinformation by providing users with tools to verify news articles and stay informed about current events. It combines machine learning-based classification, news aggregation, and advanced search capabilities to create a powerful platform for information verification and consumption.

## Features

### User Authentication

- **Registration**: Users can create accounts with lowercase usernames, email addresses, and secure passwords.
- **Login/Logout**: Secure authentication system for user access.
- **Password Reset**: Users can reset their passwords using a security key.
- **Profile Management**: Users can view and edit their profile information.

### Fake News Classification

- **Text Input**: Users can input news article text for classification.
- **Machine Learning Model**: Utilizes a pre-trained model to classify news as potentially fake or genuine.
- **Confidence Score**: Provides a confidence percentage for the classification result.

### News Aggregation

- **Latest News**: Fetches and displays the most recent news articles from various sources.
- **Categorized News**: Offers news articles sorted by categories (e.g., Business, Technology, Health).
- **Live News Updates**: Provides real-time news updates.

### Semantic Search

- **Advanced Search Algorithm**: Implements TF-IDF and cosine similarity for semantic searching of news articles.
- **Relevance Ranking**: Returns search results ranked by relevance to the user's query.

### PDF Chat

- **PDF Upload**: Users can upload PDF documents for analysis.
- **AI-Powered Chat**: Utilizes Google's Gemini AI model to answer questions about the uploaded PDF content.
- **Conversation History**: Maintains a history of questions and answers for each user.

### User Profiles

- **Customizable Information**: Users can add and edit personal details, including profile pictures.
- **Activity Tracking**: Keeps track of user interactions with the platform.

### Feedback System

- **User Ratings**: Allows users to rate their experience with the platform.
- **Feedback Submission**: Users can submit detailed feedback to improve the service.

## Technologies Used

- **Backend**: Django 3.2.10 (Python web framework)
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Database**: SQLite (default), can be configured for PostgreSQL
- **Machine Learning**: Scikit-learn, Sentence Transformers
- **Natural Language Processing**: NLTK
- **Vector Database**: FAISS for efficient similarity search
- **API Integration**: News API for fetching current news articles
- **AI Model**: Google's Gemini AI through the `google-generativeai` library
- **PDF Processing**: PyPDF2 for extracting text from PDFs
- **Authentication**: Django's built-in authentication system
