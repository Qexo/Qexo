from django.apps import AppConfig


class QexoOauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hexoweb.libs.oauth'
    verbose_name = 'Qexo OAuth/OIDC Module'

    def ready(self):
        pass
