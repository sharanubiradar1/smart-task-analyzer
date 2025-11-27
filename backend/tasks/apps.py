from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'Task Management'

    def ready(self):
        """
        Import signals or perform startup tasks here if needed.
        """
        pass