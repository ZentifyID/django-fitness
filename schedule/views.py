from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Schedule, Booking, Trainer, Activity, TrainerReview
from .forms import TrainerReviewForm
from django.db.models import Q, Avg

def schedule_list(request):
    now = timezone.now()
    schedules = Schedule.objects.filter(start_time__gte=now).order_by('start_time')
    
    # Получаем параметры фильтрации
    trainer_id = request.GET.get('trainer')
    activity_id = request.GET.get('activity')
    time_of_day = request.GET.get('time_of_day')
    
    if trainer_id:
        schedules = schedules.filter(trainer_id=trainer_id)
    
    if activity_id:
        schedules = schedules.filter(activity_id=activity_id)
        
    if time_of_day:
        if time_of_day == 'morning':
            schedules = schedules.filter(start_time__hour__gte=6, start_time__hour__lt=12)
        elif time_of_day == 'afternoon':
            schedules = schedules.filter(start_time__hour__gte=12, start_time__hour__lt=18)
        elif time_of_day == 'evening':
            schedules = schedules.filter(start_time__hour__gte=18, start_time__hour__lt=24)

    trainers = Trainer.objects.all()
    activities = Activity.objects.all()
    
    return render(request, 'schedule/schedule_list.html', {
        'schedules': schedules,
        'trainers': trainers,
        'activities': activities,
        'selected_trainer': trainer_id,
        'selected_activity': activity_id,
        'selected_time': time_of_day
    })

def trainer_list(request):
    # Аннотируем каждого тренера средним рейтингом
    trainers = Trainer.objects.annotate(avg_rating=Avg('reviews__rating'))
    form = TrainerReviewForm()
    return render(request, 'schedule/trainer_list.html', {
        'trainers': trainers,
        'form': form
    })

@login_required
def add_review(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    if request.method == 'POST':
        # Проверяем, не оставлял ли пользователь уже отзыв
        if TrainerReview.objects.filter(trainer=trainer, user=request.user).exists():
            messages.warning(request, 'Вы уже оставили отзыв об этом тренере.')
            return redirect('schedule:trainers')
            
        form = TrainerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.trainer = trainer
            review.user = request.user
            review.save()
            messages.success(request, f'Ваш отзыв о тренере {trainer.name} успешно добавлен!')
        else:
            messages.error(request, 'Ошибка при добавлении отзыва.')
    return redirect('schedule:trainers')

@login_required
def book_class(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    # Проверка наличия абонемента
    profile = request.user.profile
    if profile.is_frozen:
        messages.error(request, 'Ваш абонемент заморожен. Разморозьте его в личном кабинете для записи.')
        return redirect('members:dashboard')
        
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
