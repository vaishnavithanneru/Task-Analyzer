from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
import os


def serve_frontend(request):
    frontend_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'index.html')
    with open(frontend_path, 'r', encoding='utf-8') as f:
        return HttpResponse(f.read())

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),
    path('', serve_frontend),  # Serves frontend/index.html at root
]