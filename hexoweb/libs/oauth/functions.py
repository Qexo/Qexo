import copy
import logging
from typing import Optional, Literal, Dict

from authlib.integrations.base_client import OAuthError

from . import __oauth_manager, __provider_objects, SUPPORTED_TYPES, __provider_configs, __sso_only
from .OAuthProvider import OAuthProvider
from .models import OAuthIdentity


def get_oauth_providers_object() -> Optional[Dict[str, OAuthProvider]]:
    """
    Obtain OAuth providers object for authorization
    """

    if __provider_objects != {}:
        return __provider_objects

    if __provider_configs != {}:
        try:
            providers_config = __provider_configs
            for provider_name in providers_config:
                provider_config = providers_config[provider_name]
                __provider_objects[provider_name] = SUPPORTED_TYPES[provider_config['type']](__oauth_manager,
                                                                                             provider_name,
                                                                                             **provider_config['info'])
            return __provider_objects

        except Exception as error:
            logging.error(f"{repr(error)}")
            raise OAuthError(repr(error))

    else:
        return None


def get_oauth_providers_list() -> Dict[Optional[str], Optional[str]]:
    """
    Obtain OAuth Providers for html
    """
    if __provider_configs != {}:
        provider_data = copy.deepcopy(__provider_configs)
        for provider_name in provider_data:
            del provider_data[provider_name]['info']
            del provider_data[provider_name]['type']
        return provider_data
    else:
        return {}


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
