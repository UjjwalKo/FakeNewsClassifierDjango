from django.urls import path
from . import views

urlpatterns = [
    path('', views.pdf_chat, name='pdf_chat'),
]