from django.test import TestCase
from .scoring import calculate_priority_score
from datetime import date, timedelta


class ScoringTests(TestCase):

    def test_overdue_task_gets_huge_boost(self):
        task = {
            "id": "1",
            "title": "Overdue Task",
            "due_date": (date.today() - timedelta(days=5)).isoformat(),  # 5 days overdue
            "importance": 6,
            "estimated_hours": 3,
            "dependencies": []
        }
        # Default strategy = smart_balance
        result = calculate_priority_score(task, "smart_balance", [task])
        self.assertGreater(result["score"], 800)  # Overdue gives massive boost

    def test_quick_task_gets_bonus_in_fastest_wins(self):
        task = {
            "id": "1",
            "title": "Quick Win",
            "estimated_hours": 1,
            "importance": 5,
            "due_date": None,
            "dependencies": []
        }
        result = calculate_priority_score(task, "fastest_wins", [task])
        self.assertGreater(result["score"], 200)  # Quick tasks = high in fastest_wins

    def test_blocking_task_gets_priority(self):
        tasks = [
            {"id": "1", "title": "Foundation Task", "dependencies": []},
            {"id": "2", "title": "Blocked Task", "dependencies": ["1"]},
            {"id": "3", "title": "Another", "dependencies": []}
        ]
        # Task 1 blocks others → should get priority
        result = calculate_priority_score(tasks[0], "smart_balance", tasks)
        explanation = result["explanation"].lower()
        self.assertTrue("block" in explanation or "dependency" in explanation or "critical path" in explanation)
        self.assertGreater(result["score"], 300)