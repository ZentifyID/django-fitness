from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Schedule, Booking, Trainer

def schedule_list(request):
    # Показываем только будущие занятия, сортируем по времени
    schedules = Schedule.objects.filter(start_time__gte=timezone.now()).order_by('start_time')
    return render(request, 'schedule/schedule_list.html', {'schedules': schedules})

def trainer_list(request):
    trainers = Trainer.objects.all()
    return render(request, 'schedule/trainer_list.html', {'trainers': trainers})

@login_required
def book_class(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    # Проверка наличия абонемента
    profile = request.user.profile
    if not profile.membership or not profile.membership_expires or profile.membership_expires < timezone.now().date():
        messages.error(request, 'Для записи на занятие необходим активный абонемент!')
        return redirect('pricing')
    
    # Проверка на наличие мест
    current_bookings = schedule.bookings.count()
    if current_bookings >= schedule.capacity:
        messages.error(request, 'К сожалению, мест больше нет.')
        return redirect('schedule:list')
        
    # Проверка, не записан ли уже пользователь
    if Booking.objects.filter(schedule=schedule, user=request.user).exists():
        messages.warning(request, 'Вы уже записаны на это занятие.')
        return redirect('schedule:list')
        
    # Создание бронирования
    Booking.objects.create(schedule=schedule, user=request.user)
    messages.success(request, f'Вы успешно записаны на {schedule.activity.name}!')
    return redirect('schedule:list')
