from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def dashboard_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'accounts/dashboard.html', {'profile': profile})


@login_required
def add_test_money(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.balance += 100
    profile.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard')) 