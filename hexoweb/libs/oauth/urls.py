from django.urls import path

from .api import oauth_callback, oauth_list, oauth_link, oauth_unlink, oauth_login

urlpatterns = [
    path('api/oauth/callback/<str:provider_name>', oauth_callback, name='oauth_callback'),
    path('api/oauth/list', oauth_list, name='oauth_list'),
    path('api/oauth/link/<str:provider_name>', oauth_link, name="oauth_link"),
    path('api/oauth/unlink/<str:provider_name>', oauth_unlink, name="oauth_unlink"),
    path('api/oauth/login/<str:provider_name>', oauth_login, name="oauth_login"),
]
