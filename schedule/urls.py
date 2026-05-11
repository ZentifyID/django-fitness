from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_list, name='list'),
    path('trainers/', views.trainer_list, name='trainers'),
    path('book/<int:schedule_id>/', views.book_class, name='book'),
]
