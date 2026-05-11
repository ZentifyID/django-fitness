from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import index, pricing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('pricing/', pricing, name='pricing'),
    path('schedule/', include('schedule.urls', namespace='schedule')),
    path('members/', include('members.urls', namespace='members')),
    path('blog/', include('blog.urls', namespace='blog')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
