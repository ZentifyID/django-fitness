from django.contrib import admin
from django.urls import path, include
from core.views import index, pricing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('pricing/', pricing, name='pricing'),
    path('schedule/', include('schedule.urls', namespace='schedule')),
    path('members/', include('members.urls', namespace='members')),
    path('blog/', include('blog.urls', namespace='blog')),
]
