from hexoweb.views import *
from django.urls import path, re_path
from django.contrib.auth.views import LogoutView
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("init/", init_view, name="init"),
    path('', index, name='home'),

    path('api/save/', save, name='save'),
    path('api/new/', new, name='new'),
    path('api/delete/', delete, name='delete'),
    path('api/upload/', upload_img, name='upload'),
    path('api/delete_img/', delete_img, name='delete_img'),
    path('api/set_github/', set_github, name='set_github'),
    path('api/set_user/', set_user, name='set_user'),
    path('api/set_image_bed/', set_image_bed, name='set_image_bed'),
    path('api/purge/', purge, name='purge'),

    re_path(r'^.*\.*', pages, name='pages'),
]
