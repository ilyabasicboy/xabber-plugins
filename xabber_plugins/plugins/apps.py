from django.apps import AppConfig


class PluginsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xabber_plugins.plugins'

    def ready(self):
        super(PluginsConfig, self).ready()
        import xabber_plugins.plugins.signals
