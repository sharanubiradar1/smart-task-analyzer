from django.contrib import admin
from .models import Task, TaskDependency


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Task model.
    """
    list_display = ('title', 'due_date', 'estimated_hours', 'importance', 'created_at')
    list_filter = ('importance', 'due_date', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'due_date')
        }),
        ('Metrics', {
            'fields': ('estimated_hours', 'importance')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    """
    Admin interface for TaskDependency model.
    """
    list_display = ('task', 'depends_on')
    list_filter = ('task', 'depends_on')
    search_fields = ('task__title', 'depends_on__title')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('task', 'depends_on')