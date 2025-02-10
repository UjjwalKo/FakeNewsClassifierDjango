from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm, PasswordResetForm
from .models import Feedback
from django.http import JsonResponse

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Registration successful. Your unique code is: {user.unique_code}. Do not share this code with anyone.')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in.')
            return redirect('classify_news')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required
def feedback_view(request):
    if request.method == 'POST':
        content = request.POST.get('feedback')
        rating = request.POST.get('rating')
        if content and rating:
            Feedback.objects.create(user=request.user, content=content, rating=rating)
            messages.success(request, 'Thank you for your feedback!')
            return redirect('classify_news')
        else:
            messages.error(request, 'Please provide both a rating and feedback.')
    return render(request, 'accounts/feedback.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        unique_code = request.POST.get('unique_code')
        try:
            user = User.objects.get(email=email, unique_code=unique_code)
            return redirect('reset_password', email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or unique code.')
    return render(request, 'accounts/forgot_password.html')

def reset_password(request, email):
    user = get_object_or_404(User, email=email)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'accounts/reset_password.html', {'form': form, 'email': email}) 

@login_required
def settings_view(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Verify old password
        if not user.check_password(old_password):
            return JsonResponse({'status': 'error', 'message': 'Current password is incorrect.'})

        # Check if new passwords match
        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'New passwords do not match.'})

        # Validate new password length
        if len(new_password) < 8:
            return JsonResponse({'status': 'error', 'message': 'New password must be at least 8 characters long.'})

        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        return JsonResponse({'status': 'success', 'message': 'Your password has been changed successfully.'})

    return render(request, 'accounts/settings.html')