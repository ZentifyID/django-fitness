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
    
    def __str__(self):
        return f"Профиль {self.user.username}"
        
    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"
