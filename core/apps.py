from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    :depends-on: martor, django.contrib.auth, django.contrib.messages, django.contrib.admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
