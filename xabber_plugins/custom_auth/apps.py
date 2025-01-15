from django.apps import AppConfig


class CustomAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xabber_plugins.custom_auth'
