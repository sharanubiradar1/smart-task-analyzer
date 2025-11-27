from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Task(models.Model):
    """
    Task model representing a single task with priority scoring attributes.
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Estimated hours to complete the task"
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Importance rating from 1-10"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TaskDependency(models.Model):
    """
    Represents dependencies between tasks.
    """
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='dependencies_out'
    )
    depends_on = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='dependencies_in'
    )

    class Meta:
        unique_together = ('task', 'depends_on')
        verbose_name_plural = 'Task dependencies'

    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on.title}"