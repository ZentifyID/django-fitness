from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_list, name='list'),
    path('trainers/', views.trainer_list, name='trainers'),
    path('trainer/<int:trainer_id>/review/', views.add_review, name='add_review'),
    path('book/<int:schedule_id>/', views.book_class, name='book'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel'),
]
