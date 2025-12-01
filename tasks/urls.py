# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list),
    path('create/', views.create_task),
    path('add/', views.add_task),
    path('delete/<int:pk>/', views.delete_task),
    
    path('analyze/', views.analyze_tasks),
    path('suggest/', views.suggest_today),
]