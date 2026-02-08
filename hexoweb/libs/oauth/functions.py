from typing import Literal, Dict

from django.template.defaulttags import register

from . import __oauth_manager, __sso_only
from .OAuthProvider import OAuthProvider, SUPPORTED_TYPES
from .models import OAuthIdentity, OAuthProviderModel


def get_oauth_providers_object() -> Dict[str, OAuthProvider]:
    providers = OAuthProviderModel.objects.all()
    provider_objects: Dict[str, OAuthProvider] = {}
    for provider in providers:
        provider_objects[provider.name] = SUPPORTED_TYPES[provider.type](__oauth_manager, provider)
    return provider_objects


@register.filter
def get_oauth_providers_list(include_configs=False) -> Dict[str, Dict[str, str]]:
    """
    :param include_configs: Whether to include provider`s config in the output

    Obtain configured OAuth providers list
    Like this:
    {
    "provider_name": {
        "friendly_name": "Friendly Name",
        "icon": "http://icon.url/icon.png",
        "client_id": "xxxx",            # Only when include_configs is True
        "client_secret": "******",    # Only when include_configs is True, it`s always '******'
        "type": "Type",                # Only when include_configs is True
        "scope": "Scope",              # Only when include_configs is True
        "server_metadata_url": "URL"   # Only when include_configs is True
        },
    }
    """
    providers = OAuthProviderModel.objects.all()
    providers_list: Dict[str, Dict[str, str]] = {}
    for provider in providers:
        providers_list[provider.name] = {
            'friendly_name': provider.friendly_name,
            'icon': provider.icon
        }
        if include_configs: providers_list[provider.name] = {
            **providers_list[provider.name],
            'client_id': provider.client_id,
            'client_secret': '******',
            'type': provider.type,
            'scope': provider.scope,
            'server_metadata_url': provider.server_metadata_url
        }
    return providers_list


@register.filter
def get_oauth_supported_provider_types() -> Dict[str, Dict[str, str]]:
    """
    Obtain supported OAuth provider types and their all required settings
    Like this:
    {
    "GitHub": {
        "name": "Name",
        "friendly_name": "Friendly Name",
        "icon": "Icon",
        "client_id": "Client ID",
        "client_secret": "Client Secret",
        "scope": "Scope"
        },
    }
    """
    supported_provider_types: Dict[str, Dict[str, str]] = {}
    for provider_type in OAuthProvider.__subclasses__():
        supported_provider_types[provider_type.__name__] = provider_type.SETTINGS
    return supported_provider_types


def create_oauth_callback_action(request, status: bool, message: str, action: Literal['refresh', 'none']):
    """
    Create OAuth callback action
    :param request: Django request object
    :param status: Callback status
    :param message: Callback message
    :param action: Callback action, when it`s refresh, the main window will refresh
    """
    from django.shortcuts import render
    return render(request, 'oauth/oauth_callback.html', {
        'payload': {
            'status': status,
            'message': message,
            'action': action,
        }
    })


def check_sso_only() -> bool:
    return __sso_only and OAuthIdentity.objects.exists()
