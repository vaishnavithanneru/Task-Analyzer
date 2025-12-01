from datetime import date
import math

def calculate_priority_score(task, strategy="smart_balance", all_tasks=None):
    if all_tasks is None:
        all_tasks = []

    today = date.today()
    
    # Fix: Convert string date to real date object
    due_date_str = task.get("due_date")
    if isinstance(due_date_str, str) and due_date_str:
        from datetime import datetime
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except:
            due_date = None
    else:
        due_date = due_date_str  # already a date or None

    importance = int(task.get("importance", 5))
    effort = max(1, int(task.get("estimated_hours", 1)))
    deps = task.get("dependencies", [])

    score = 0

    # 1. Urgency (highest weight)
    if due_date:
        days_left = (due_date - today).days
        if days_left < 0:
            score += 300 + abs(days_left) * 10  # Overdue = massive penalty
        elif days_left == 0:
            score += 200
        elif days_left <= 3:
            score += 120
        else:
            score += max(0, 80 - days_left)
    else:
        score += 20  # No due date = low urgency

    # 2. Importance
    score += importance * 15

    # 3. Quick wins
    if effort <= 2:
        score += 80
    elif effort <= 4:
        score += 40

    # 4. Blocks others?
    task_id = task.get("id")
    if task_id and all_tasks:
        blocked_count = sum(1 for t in all_tasks if task_id in (t.get("dependencies") or []))
        score += blocked_count * 100

    return round(score, 2)