from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    path('settings/', views.settings_view, name='settings'),
]