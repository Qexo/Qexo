"""
Custom AppConfig classes for Django built-in apps to support MongoDB.

MongoDB does not support AutoField, so we need to use ObjectIdAutoField instead.
These custom configs override the default_auto_field for built-in Django apps.
"""
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig


class MongoAuthConfig(AuthConfig):
    """Custom AuthConfig for MongoDB that uses ObjectIdAutoField"""
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'


class MongoContentTypesConfig(ContentTypesConfig):
    """Custom ContentTypesConfig for MongoDB that uses ObjectIdAutoField"""
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
