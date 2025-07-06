from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from predictions.models import Prediction
from datetime import datetime

def root(request):
    return JsonResponse({"message": "Welcome to Stock Insight Platform"})

def healthz(request):
    return JsonResponse({"status": "ok"})

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, "registration.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-requested_at')[:10]
    profile = UserProfile.objects.get(user=request.user)
    today = datetime.utcnow().date()
    used = Prediction.objects.filter(user=request.user, requested_at__date=today).count()
    quota = profile.daily_quota or 0
    is_pro = profile.is_pro
    return render(request, "dashboard.html", {
        "predictions": predictions,
        "quota": quota,
        "used": used,
        "is_pro": is_pro
    })

@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, "profile.html", {"profile": profile})