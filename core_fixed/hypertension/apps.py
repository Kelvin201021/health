from django.apps import AppConfig

class HypertensionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hypertension'

    def ready(self):
        import hypertension.signals
