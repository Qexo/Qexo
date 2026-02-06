from django.apps import AppConfig


class ConsoleConfig(AppConfig):
    # Django will use the global DEFAULT_AUTO_FIELD setting from core/settings.py
    # which is automatically configured based on the database backend
    name = 'hexoweb'
