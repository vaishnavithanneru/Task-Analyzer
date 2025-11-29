from rest_framework import serializers

class TaskInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(max_length=200)
    due_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_hours = serializers.IntegerField(min_value=1, default=1)
    importance = serializers.IntegerField(min_value=1, max_value=10, default=5)
    dependencies = serializers.JSONField(default=list)