from hexoweb.views import *
from django.urls import path, re_path
# from django.contrib import admin
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT},
            name='static'),

    path('login/', login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("init/", init_view, name="init"),
    path('', index, name='home'),

    path('api/auth/', auth, name='auth'),
    path('api/save/', save, name='save'),
    path('api/save_post/', save_post, name='save_post'),
    path('api/save_draft/', save_draft, name='save_draft'),
    path('api/new/', new, name='new'),
    path('api/delete/', delete, name='delete'),
    path('api/delete_post/', delete_post, name='delete_post'),
    path('api/upload/', upload_img, name='upload'),
    path('api/delete_img/', delete_img, name='delete_img'),
    path('api/set_github/', set_github, name='set_github'),
    path('api/set_user/', set_user, name='set_user'),
    path('api/set_image_bed/', set_image_bed, name='set_image_bed'),
    path('api/set_update/', set_update, name='set_update'),
    path('api/set_apikey/', set_api_key, name='set_apikey'),
    path('api/purge/', purge, name='purge'),
    path('api/webhook/', webhook, name='webhook'),
    path('api/create_webhook/', create_webhook_config, name='create_webhook'),
    path('api/get_update/', get_update, name='get_update'),
    path('api/do_update/', do_update, name='do_update'),

    re_path(r'^(?!api).*$\.*', pages, name='pages'),
]
