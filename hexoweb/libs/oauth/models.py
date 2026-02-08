from django.contrib.auth.models import User
from django.db import models


class OAuthIdentity(models.Model):
    provider_name = models.CharField(max_length=50, blank=False)
    provider_sub = models.CharField(max_length=255, blank=False)
    provider_preferred_username = models.CharField(max_length=50, blank=False)
    local_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oauth_identities')
    bind_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider_name', 'provider_sub')


class OAuthProviderModel(models.Model):
    name = models.CharField(max_length=50, blank=False, primary_key=True)
    type = models.CharField(max_length=50, blank=False)
    client_id = models.CharField(max_length=255, blank=False)
    client_secret = models.CharField(max_length=255, blank=False)
    server_metadata_url = models.CharField(max_length=255, blank=True)
    scope = models.CharField(max_length=255, blank=True)
    friendly_name = models.CharField(max_length=100, blank=False)
    icon = models.CharField(max_length=255, blank=False)
