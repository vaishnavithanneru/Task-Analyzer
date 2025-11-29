from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(default=1)
    importance = models.IntegerField(default=5, help_text="1-10 scale")
    dependencies = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.title} (Due: {self.due_date or 'No due date'})"