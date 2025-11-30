# tasks/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response   # ← This fixes "Response not defined"
from rest_framework import status
from .models import Task
from .scoring import calculate_priority_score
from .serializers import TaskInputSerializer
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.shortcuts import render
import os
from django.conf import settings

# Existing endpoints (keep them)
@api_view(['POST'])
def analyze_tasks(request):
    serializer = TaskInputSerializer(data=request.data, many=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    tasks = serializer.validated_data
    strategy = request.query_params.get('strategy', 'smart_balance')

    for i, task in enumerate(tasks):
        if not task.get('id'):
            task['id'] = f"temp_{i}"

    results = []
    for task in tasks:
        result = calculate_priority_score(task, strategy, tasks)
        results.append({
            **task,
            "score": result["score"],
            "explanation": result["explanation"]
        })

    sorted_tasks = sorted(results, key=lambda x: x["score"], reverse=True)
    return Response(sorted_tasks)




@api_view(['POST'])
def suggest_today(request):
    # Accept either:
    #  - JSON array in body (old frontend): request.data is a list of tasks
    #  - JSON object: { "tasks": [...], "strategy": "..." }
    raw = request.data

    # Determine tasks_payload and strategy safely
    if isinstance(raw, dict):
        tasks_payload = raw.get('tasks') or raw.get('data') or raw.get('tasks_list')
        # If no nested list found, maybe user POSTed a single task dict -> wrap it
        if tasks_payload is None:
            # If dict looks like a task (has title or importance), wrap it
            if any(k in raw for k in ('title', 'importance', 'estimated_hours', 'due_date')):
                tasks_payload = [raw]
            else:
                tasks_payload = []
        strategy = raw.get('strategy') or request.query_params.get('strategy', 'smart_balance')
    else:
        # raw is likely a list (the frontend sends an array)
        tasks_payload = raw
        strategy = request.query_params.get('strategy', 'smart_balance')

    serializer = TaskInputSerializer(data=tasks_payload, many=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    tasks = serializer.validated_data

    for i, task in enumerate(tasks):
        if not task.get('id'):
            task['id'] = f"temp_{i}"

    scored = []
    for task in tasks:
        res = calculate_priority_score(task, strategy, tasks)
        task_copy = dict(task)
        task_copy.update({"score": res["score"], "explanation": res["explanation"]})
        scored.append(task_copy)

    top_3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
    suggestions = [
        {"rank": i+1, "title": t["title"], "why": t["explanation"], "score": t["score"]}
        for i, t in enumerate(top_3)
    ]
    return Response({"today_suggestions": suggestions})


# NEW ENDPOINTS – Add these at the bottom
@api_view(['POST'])
def create_task(request):
    serializer = TaskInputSerializer(data=request.data)
    if serializer.is_valid():
        Task.objects.create(**serializer.validated_data)
        return Response({"status": "Task added!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def all_tasks(request):
    tasks = Task.objects.all()
    data = []
    for t in tasks:
        data.append({
            "id": t.id,
            "title": t.title,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "estimated_hours": t.estimated_hours,
            "importance": t.importance,
        })
    return Response(data)
@api_view(['DELETE'])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.delete()
        return Response({"status": "deleted"}, status=204)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=404)
    
def serve_frontend(request, path=''):
    if not path or path == 'index.html':
        file_path = os.path.join(settings.BASE_DIR, 'frontend', 'index.html')
    else:
        file_path = os.path.join(settings.BASE_DIR, 'frontend', path)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content_type = 'text/html'
            if path.endswith('.css'): content_type = 'text/css'
            if path.endswith('.js'): content_type = 'application/javascript'
            return HttpResponse(f.read(), content_type=content_type)
    return HttpResponse("Not found", status=404)

# PUBLIC TASK LIST — THIS SHOWS ALL TASKS
# ALSO UPDATE public_task_list() TO SHOW CURRENT STRATEGY
def public_task_list(request):
    tasks = Task.objects.all().order_by('-id')
    strategy = request.GET.get('strategy', 'smart_balance')  # Read from URL
    
    # Re-score tasks with current strategy
    task_list = []
    for t in tasks:
        task_data = {
            'id': t.id,
            'title': t.title,
            'due_date': t.due_date.isoformat() if t.due_date else None,
            'estimated_hours': t.estimated_hours,
            'importance': t.importance,
            'dependencies': []
        }
        score_info = calculate_priority_score(task_data, strategy, [task_data])
        task_list.append({
            'task': t,
            'score': score_info['score'],
            'explanation': score_info['explanation']
        })

    return render(request, 'public_tasks.html', {
        'tasks': task_list,
        'strategy': strategy.title().replace('_', ' ')
    })