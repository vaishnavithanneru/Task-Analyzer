from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import calculate_priority_score
from .serializers import TaskSerializer
from datetime import date
from .models import Task
from .serializers import TaskSerializer

@api_view(['POST'])
def analyze_tasks(request):
    strategy = request.query_params.get('strategy', 'smart_balance')
    tasks_data = request.data

    if not isinstance(tasks_data, list):
        return Response({"error": "Expected a list of tasks"}, status=400)

    enriched_tasks = []
    for task in tasks_data:
        try:
            task_copy = task.copy()
            task_copy.setdefault('id', id(task))
            score = calculate_priority_score(task_copy, strategy, tasks_data)

            explanation_parts = []
            if task.get("due_date") and task["due_date"] < date.today():
                explanation_parts.append("OVERDUE")
            if task.get("importance", 5) >= 8:
                explanation_parts.append("High importance")
            if task.get("estimated_hours", 1) <= 2:
                explanation_parts.append("Quick win")
            if any(task_copy['id'] in (t.get("dependencies") or []) for t in tasks_data):
                explanation_parts.append("Blocks other tasks")

            explanation = ", ".join(explanation_parts) or "Balanced priority"

            task_copy["score"] = score
            task_copy["explanation"] = explanation
            enriched_tasks.append(task_copy)
        except Exception as e:
            continue  # Skip invalid tasks gracefully

    enriched_tasks.sort(key=lambda x: x["score"], reverse=True)

    serializer = TaskSerializer(enriched_tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def suggest_today(request):
    # In real app: fetch from DB. Here: return mock top 3
    mock_suggestions = [
        {"title": "Fix critical production bug", "explanation": "OVERDUE, High importance, Blocks deployment"},
        {"title": "Reply to client email", "explanation": "Due today, High importance"},
        {"title": "Update README", "explanation": "Quick win, Low effort"}
    ]
    return Response(mock_suggestions[:3])

# views.py (add these)
@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
    serialized = TaskSerializer(tasks, many=True)
    enriched = []
    for item in serialized.data:
        item["score"] = calculate_priority_score(item, "smart_balance", serialized.data)
        item["explanation"] = "Smart priority"
        enriched.append(item)
    enriched.sort(key=lambda x: x["score"], reverse=True)
    return Response(enriched)

@api_view(['POST'])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        task = Task.objects.create(**serializer.validated_data)
        return Response(TaskSerializer(task).data, status=201)
    return Response(serializer.errors, status=400)
@api_view(['POST'])
def add_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # ← THIS SAVES TO db.sqlite3 PERMANENTLY
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['DELETE'])
def delete_task(request, pk):  # ← Name it delete_task
    try:
        task = Task.objects.get(pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)