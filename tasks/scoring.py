from datetime import date, timedelta
import math

STRATEGIES = {
    "smart_balance": 0,
    "fastest_wins": 1,
    "high_impact": 2,
    "deadline_driven": 3,
}

def calculate_priority_score(task_data, strategy="smart_balance", all_tasks=None):
    """
    Returns a score and explanation for a task.
    Higher score = higher priority
    """
    if all_tasks is None:
        all_tasks = []

    task_id = task_data.get("id")
    due_date_str = task_data.get("due_date")
    importance = max(1, min(10, task_data.get("importance", 5)))
    effort = max(1, task_data.get("estimated_hours", 1))
    deps = task_data.get("dependencies", [])

    today = date.today()
    explanation = []

    # Parse due date
    if due_date_str:
        try:
            due_date = date.fromisoformat(due_date_str.replace("Z", ""))
            days_until = (due_date - today).days
        except:
            days_until = 999  # far future if invalid
            explanation.append("Invalid due date → treated as not urgent")
    else:
        days_until = 999
        explanation.append("No due date → low urgency")

    urgency_score = 0
    if days_until < 0:
        urgency_score = 100 + abs(days_until) * 5
        explanation.append(f"OVERDUE by {-days_until} days → massive boost")
    elif days_until == 0:
        urgency_score = 80
        explanation.append("Due today → high urgency")
    elif days_until <= 3:
        urgency_score = 60 - days_until * 10
        explanation.append(f"Due in {days_until} days → urgent")
    elif days_until <= 7:
        urgency_score = 30
        explanation.append("Due this week")

    # Dependency blocking score
    blocking_score = 0
    if all_tasks:
        blocked_count = sum(1 for t in all_tasks if str(task_id) in t.get("dependencies", []))
        if blocked_count > 0:
            blocking_score = blocked_count * 30
            explanation.append(f"Blocks {blocked_count} other task(s) → priority boost")

    # Base scores
    importance_score = importance * 12
    effort_score = max(1, 20 - effort * 3)  # lower effort = higher score

    # Strategy-specific weighting
    strategy = strategy.lower()
    if strategy == "fastest_wins":
        score = effort_score * 5 + importance_score * 2 + urgency_score
        explanation.insert(0, "Fastest Wins mode: low effort prioritized")
    elif strategy == "high_impact":
        score = importance_score * 8 + blocking_score * 2 + urgency_score
        explanation.insert(0, "High Impact mode: importance dominates")
    elif strategy == "deadline_driven":
        score = urgency_score * 10 + importance_score * 2 + blocking_score
        explanation.insert(0, "Deadline Driven: urgency first")
    else:  # smart_balance (default)
        score = (
            urgency_score * 4 +
            importance_score * 3 +
            effort_score * 2 +
            blocking_score * 3
        )
        explanation.insert(0, "Smart Balance: balanced factors")

    # Overdue tasks always rise to top
    if days_until < 0:
        score += 1000

    return {
        "score": round(score, 2),
        "explanation": "; ".join(explanation) or "Standard priority"
    }