from django.apps import AppConfig


class QuestionnaireConfig(AppConfig):
    """
    :depends-on: django.contrib.auth, django.contrib.messages, django.contrib.admin
    """    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'questionnaire'
