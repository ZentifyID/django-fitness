from django.db import models
from django.contrib.auth.models import User

class MembershipPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    description = models.TextField(verbose_name="Описание", blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    duration_days = models.PositiveIntegerField(verbose_name="Длительность (дней)")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    membership = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Абонемент")
    membership_expires = models.DateField(null=True, blank=True, verbose_name="Годен до")
    is_frozen = models.BooleanField(default=False, verbose_name="Заморожен")
    freeze_start = models.DateField(null=True, blank=True, verbose_name="Дата начала заморозки")
    
    def __str__(self):
        return f"Профиль {self.user.username}"
        
    def days_left(self):
        from django.utils import timezone
        if self.membership_expires:
            delta = self.membership_expires - timezone.now().date()
            return max(0, delta.days)
        return 0

    def membership_progress(self):
        if self.membership and self.membership_expires:
            total = self.membership.duration_days
            left = self.days_left()
            if total > 0:
                # Процент пройденного времени (от 0 до 100)
                # Если осталось 30 дней из 30, прогресс 0% (или 100%?). 
                # Обычно прогресс-бар показывает сколько "пройдено". 
                # Давайте показывать сколько "осталось" или сколько "прошло".
                # Лучше показывать сколько ОСТАЛОСЬ визуально, или сколько ПРОШЛО.
                # Сделаем "процент оставшегося", так нагляднее для "статуса абонемента".
                return min(100, int((left / total) * 100))
        return 0

    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"
