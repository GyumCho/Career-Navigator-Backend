from django.apps import AppConfig

class JobsConfig(AppConfig):
    """
    :depends-on: core, questionnaire, martor, django.contrib.auth, django.contrib.messages, django.contrib.admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
