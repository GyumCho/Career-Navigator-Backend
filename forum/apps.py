from django.apps import AppConfig


class ForumConfig(AppConfig):
    """
    App definition of the Core App

    :depends-on: martor, core, django.contrib.admin, django.contrib.messages
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forum'
