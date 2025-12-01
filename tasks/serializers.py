from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies']
        read_only_fields = ['id']

    # ← THIS IS THE FIX — ADD THESE 2 METHODS
    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.estimated_hours = validated_data.get('estimated_hours', instance.estimated_hours)
        instance.importance = validated_data.get('importance', instance.importance)
        instance.dependencies = validated_data.get('dependencies', instance.dependencies)
        instance.save()
        return instance