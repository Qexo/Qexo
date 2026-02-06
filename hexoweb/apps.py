from django.apps import AppConfig
from django.conf import settings


class ConsoleConfig(AppConfig):
    # Use ObjectIdAutoField for MongoDB, BigAutoField for other databases
    @property
    def default_auto_field(self):
        if hasattr(settings, 'DATABASES') and settings.DATABASES.get('default', {}).get('ENGINE') == 'django_mongodb_backend':
            return 'django_mongodb_backend.fields.ObjectIdAutoField'
        return 'django.db.models.BigAutoField'
    
    name = 'hexoweb'
