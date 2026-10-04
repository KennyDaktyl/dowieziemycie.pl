from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.content'
    verbose_name = 'Treści'

    def ready(self):
        from .revalidation import connect_signals

        connect_signals()
