from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime
from .models import MemberProfile, MembershipPlan
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

@login_required
def payment_page(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id)
    if request.method == 'POST':
        # "Оплата" прошла успешно
        profile = request.user.profile
        profile.membership = plan
        # Если абонемент уже есть и он еще действует, можно прибавлять дни, но мы для простоты перезаписываем с сегодняшнего дня
        profile.membership_expires = timezone.now().date() + datetime.timedelta(days=plan.duration_days)
        profile.save()
        
        messages.success(request, f'Вы успешно приобрели тариф "{plan.name}"!')
        return redirect('members:dashboard')
        
    return render(request, 'members/payment.html', {'plan': plan})
