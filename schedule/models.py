from django.db import models
from django.contrib.auth.models import User

class Trainer(models.Model):
    name = models.CharField(max_length=150, verbose_name="ФИО тренера")
    specialization = models.CharField(max_length=200, verbose_name="Специализация")
    bio = models.TextField(verbose_name="О себе", blank=True)
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True, verbose_name="Фото")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренеры"

class Activity(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название занятия")
    description = models.TextField(verbose_name="Описание")
    duration_minutes = models.PositiveIntegerField(verbose_name="Длительность (мин)", default=60)
    color = models.CharField(max_length=20, default="#4CAF50", verbose_name="Цвет в расписании")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид занятия"
        verbose_name_plural = "Виды занятий"

class Schedule(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="Занятие")
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Тренер")
    start_time = models.DateTimeField(verbose_name="Время начала")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость", default=10)

    def __str__(self):
        return f"{self.activity.name} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "Элемент расписания"
        verbose_name_plural = "Расписание"

class Booking(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='bookings', verbose_name="Занятие в расписании")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")

    def __str__(self):
        return f"{self.user.username} -> {self.schedule}"

    class Meta:
        verbose_name = "Запись на занятие"
        verbose_name_plural = "Записи на занятия"
        unique_together = ('schedule', 'user')
