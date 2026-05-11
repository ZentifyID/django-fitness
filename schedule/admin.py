from django.contrib import admin
from .models import Trainer, Activity, Schedule, Booking

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization')
    search_fields = ('name',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'trainer', 'start_time', 'capacity')
    list_filter = ('start_time', 'activity', 'trainer')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'created_at')
    list_filter = ('schedule__start_time',)
