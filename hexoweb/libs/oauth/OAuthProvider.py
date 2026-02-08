from abc import ABC, abstractmethod
from typing import Dict, Type

from authlib.integrations.django_client import OAuth
from authlib.oidc.core import UserInfo

from hexoweb.functions import gettext
from .models import OAuthProviderModel


class OAuthProvider(ABC):
    SETTINGS: dict = {
        'name': gettext('OAUTH_PROVIDER_NAME'),
        'client_id': gettext('OAUTH_PROVIDER_CLIENT_ID'),
        'client_secret': gettext('OAUTH_PROVIDER_CLIENT_SECRET'),
        'scope': gettext('OAUTH_PROVIDER_SCOPE'),
        'friendly_name': gettext('OAUTH_PROVIDER_CLIENT_FRIENDLY_NAME'),
        'icon': gettext('OAUTH_PROVIDER_CLIENT_ICON'),
    }

    def __init__(self, oauth_manager: OAuth, model: OAuthProviderModel) -> None:
        self.model = model
        self.oauth_manager = oauth_manager
        self.name = model.name

    def authorize_redirect(self, request, redirect_uri):
        return self.oauth_manager.create_client(self.name).authorize_redirect(request, redirect_uri)

    def authorize_access_token(self, request):
        return self.oauth_manager.create_client(self.name).authorize_access_token(request)

    @abstractmethod
    def userinfo(self, token: str) -> UserInfo:
        """
        Please ensure UserInfo.sub and UserInfo.preferred_username are defined
        Like this:
        user = UserInfo()
        user.sub = 'xxxx'
        user.preferred_username = 'xxxx'
        """
        pass


class OIDC(OAuthProvider):
    SETTINGS = {**OAuthProvider.SETTINGS,
                'server_metadata_url': gettext('OIDC_PROVIDER_SERVER_METADATA_URL')}

    def __init__(self, oauth_manager: OAuth, modal: OAuthProviderModel) -> None:
        super().__init__(oauth_manager, modal)
        build_payloads = {
            'client_id': modal.client_id,
            'client_secret': modal.client_secret,
            'server_metadata_url': modal.server_metadata_url,
            "client_kwargs": {
                "scope": modal.scope
            }

        }
        self.oauth_manager.register(name=self.name, **build_payloads)

    def userinfo(self, token: str) -> UserInfo:
        return self.oauth_manager.create_client(self.name).userinfo(token=token)


class GitHub(OAuthProvider):

    def __init__(self, oauth_manager: OAuth, modal: OAuthProviderModel) -> None:
        super().__init__(oauth_manager, modal)
        build_payload = {
            "client_id": modal.client_id,
            "client_secret": modal.client_secret,
            "client_kwargs": {
                "scope": modal.scope
            }
        }
        oauth_manager.register(name=self.name,
                               access_token_url='https://github.com/login/oauth/access_token',
                               access_token_params=None,
                               authorize_url='https://github.com/login/oauth/authorize',
                               authorize_params=None,
                               api_base_url='https://api.github.com/',
                               **build_payload)

    def userinfo(self, token: str) -> UserInfo:
        resp = self.oauth_manager.create_client(self.name).get('user', token=token)
        resp.raise_for_status()
        user = UserInfo()
        user.sub = str(resp.json()['id'])
        user.preferred_username = str(resp.json()['login'])
        return user


SUPPORTED_TYPES: Dict[str, Type[OAuthProvider]] = {
    "github": GitHub,
    "oidc": OIDC
}
