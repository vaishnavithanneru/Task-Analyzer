from django.test import TestCase
from .scoring import calculate_priority_score
from datetime import date, timedelta

class ScoringTests(TestCase):
    def test_overdue_task_gets_huge_boost(self):
        task = {
            "id": "1",
            "title": "Old task",
            "due_date": (date.today() - timedelta(days=5)).isoformat(),
            "importance": 5,
            "estimated_hours": 3,
            "dependencies": []
        }
        result = calculate_priority_score(task)
        self.assertGreater(result["score"], 1000)

    def test_quick_task_gets_bonus_in_fastest_wins(self):
        task = {"id": "1", "title": "Quick", "estimated_hours": 1, "importance": 5, "dependencies": []}
        score = calculate_priority_score(task, "fastest_wins")["score"]
        self.assertGreater(score, 150)

    def test_blocking_task_gets_priority(self):
        tasks = [
            {"id": "1", "title": "A", "dependencies": []},
            {"id": "2", "title": "B", "dependencies": ["1"]}
        ]
        score = calculate_priority_score(tasks[0], all_tasks=tasks)["score"]
        self.assertIn("Blocks", calculate_priority_score(tasks[0], all_tasks=tasks)["explanation"])