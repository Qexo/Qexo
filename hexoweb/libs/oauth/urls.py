from django.urls import path

from .api import oauth_callback, oauth_list, oauth_link, oauth_unlink, oauth_login, set_oauth_providers,get_oauth_providers

urlpatterns = [
    path('callback/<str:provider_name>', oauth_callback, name='oauth_callback'),
    path('list', oauth_list, name='oauth_list'),
    path('link/<str:provider_name>', oauth_link, name="oauth_link"),
    path('unlink/<str:provider_name>', oauth_unlink, name="oauth_unlink"),
    path('login/<str:provider_name>', oauth_login, name="oauth_login"),
    path('set_providers', set_oauth_providers, name="set_oauth_providers"),
    path('get_providers', get_oauth_providers, name="get_oauth_providers"),
]
