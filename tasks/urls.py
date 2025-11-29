from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_tasks),
    path('suggest/', views.suggest_today),
    path('create/', views.create_task),
    path('all/', views.all_tasks),
    path('delete/<int:task_id>/', views.delete_task),
]