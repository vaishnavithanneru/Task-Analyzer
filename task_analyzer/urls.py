# task_analyzer/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
import os
from django.conf import settings
from tasks import views

# This serves your frontend files directly — no template needed!
def serve_frontend(request, path=''):
    if path == '' or path == 'index.html':
        file_path = os.path.join(settings.BASE_DIR, 'frontend', 'index.html')
    else:
        file_path = os.path.join(settings.BASE_DIR, 'frontend', path)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type={
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
            }.get(os.path.splitext(file_path)[1], 'application/octet-stream'))
    else:
        return HttpResponse("File not found", status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),
    path('public-tasks/', views.public_task_list),
    path('', views.serve_frontend),                    # http://127.0.0.1:8000/
    path('<path:path>', views.serve_frontend),         # For style.css, script.js, etc.
    
]
