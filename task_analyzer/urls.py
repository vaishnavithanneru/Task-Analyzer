from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static   # ← ADD THIS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    path('public-tasks/', TemplateView.as_view(template_name='public_tasks.html')),
]

# ← THIS MAKES CSS & JS WORK IN DEVELOPMENT →
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])