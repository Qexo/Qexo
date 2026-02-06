from abc import ABC, abstractmethod

from authlib.integrations.django_client import OAuth
from authlib.oidc.core import UserInfo


class OAuthProvider(ABC):
    def __init__(self, oauth_manager: OAuth, name: str, **kwargs) -> None:
        self.oauth_manager = oauth_manager
        self.name = name

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
    def __init__(self, oauth_manager: OAuth, name: str, **kwargs) -> None:
        super().__init__(oauth_manager, name)
        self.oauth_manager.register(name=self.name, **kwargs)

    def userinfo(self, token: str) -> UserInfo:
        return self.oauth_manager.create_client(self.name).userinfo(token=token)


class GitHub(OAuthProvider):

    def __init__(self, oauth_manager: OAuth, name: str, **kwargs) -> None:
        super().__init__(oauth_manager, name)
        oauth_manager.register(name=self.name,
                               access_token_url='https://github.com/login/oauth/access_token',
                               access_token_params=None,
                               authorize_url='https://github.com/login/oauth/authorize',
                               authorize_params=None,
                               api_base_url='https://api.github.com/',
                               **kwargs)

    def userinfo(self, token: str) -> UserInfo:
        resp = self.oauth_manager.create_client(self.name).get('user', token=token)
        resp.raise_for_status()
        user = UserInfo()
        user.sub = str(resp.json()['id'])
        user.preferred_username = str(resp.json()['login'])
        return user
