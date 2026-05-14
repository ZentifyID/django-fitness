from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime
from .models import MemberProfile, MembershipPlan
from schedule.models import Booking

from .forms import MemberRegistrationForm, ProfileUpdateForm

def register_view(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = form.cleaned_data.get('phone')
            MemberProfile.objects.create(user=user, phone=phone)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('members:dashboard')
    else:
        form = MemberRegistrationForm()
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
    
    # Разделяем записи на будущие и прошедшие
    now = timezone.now()
    upcoming_bookings = Booking.objects.filter(
        user=request.user, 
        schedule__start_time__gte=now
    ).order_by('schedule__start_time')
    
    past_bookings = Booking.objects.filter(
        user=request.user, 
        schedule__start_time__lt=now
    ).order_by('-schedule__start_time')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('members:dashboard')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'members/dashboard.html', {
        'profile': profile,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'form': form,
        'now': now
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

@login_required
def toggle_freeze(request):
    profile = request.user.profile
    if not profile.membership:
        messages.error(request, 'У вас нет активного абонемента для заморозки.')
        return redirect('members:dashboard')
        
    if profile.is_frozen:
        # Размораживаем
        today = timezone.now().date()
        freeze_days = (today - profile.freeze_start).days
        if freeze_days > 0:
            profile.membership_expires += datetime.timedelta(days=freeze_days)
        
        profile.is_frozen = False
        profile.freeze_start = None
        profile.save()
        messages.success(request, f'Абонемент разморожен! Срок действия продлен на {max(0, freeze_days)} дн.')
    else:
        # Замораживаем
        # 1. Отменяем все будущие записи, чтобы освободить места
        now = timezone.now()
        upcoming_bookings = Booking.objects.filter(
            user=request.user, 
            schedule__start_time__gte=now
        )
        cancelled_count = upcoming_bookings.count()
        upcoming_bookings.delete()

        # 2. Устанавливаем статус
        profile.is_frozen = True
        profile.freeze_start = now.date()
        profile.save()
        
        msg = 'Абонемент заморожен. Вы не сможете записываться на занятия.'
        if cancelled_count > 0:
            msg += f' Ваши будущие записи ({cancelled_count}) были отменены.'
        messages.warning(request, msg)
        
    return redirect('members:dashboard')
