from rest_framework import serializers
from .models import Task, TaskDependency


class TaskInputSerializer(serializers.Serializer):
    """
    Serializer for task input data (non-model based for flexibility).
    """
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField(min_value=0.1)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    task_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_estimated_hours(self, value):
        """Ensure estimated hours is reasonable."""
        if value > 1000:
            raise serializers.ValidationError(
                "Estimated hours seems unreasonably high (>1000 hours)"
            )
        return value

    def validate_dependencies(self, value):
        """Ensure dependencies list doesn't contain duplicates."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Dependencies list contains duplicates"
            )
        return value


class TaskOutputSerializer(serializers.Serializer):
    """
    Serializer for task output with priority score.
    """
    task_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.IntegerField())
    priority_score = serializers.FloatField()
    priority_level = serializers.CharField()
    explanation = serializers.CharField()


class SuggestedTaskSerializer(serializers.Serializer):
    """
    Serializer for suggested tasks with detailed explanations.
    """
    task_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    priority_score = serializers.FloatField()
    reason = serializers.CharField()
    action_items = serializers.ListField(child=serializers.CharField())