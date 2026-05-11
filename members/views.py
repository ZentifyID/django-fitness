from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MemberProfile
from schedule.models import Booking

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            MemberProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('members:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'members/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('members:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'members/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.info(request, 'Вы успешно вышли из системы.')
        return redirect('index')

@login_required
def dashboard(request):
    profile, created = MemberProfile.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(user=request.user).order_by('schedule__start_time')
    return render(request, 'members/dashboard.html', {
        'profile': profile,
        'bookings': bookings
    })
