from django.db import models
from django.contrib import admin
from .models import MembershipPlan, MemberProfile

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'membership', 'membership_expires')
    search_fields = ('user__username', 'phone')
