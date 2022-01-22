from hexoweb.views import *
from django.urls import path, re_path
# from django.contrib import admin
from django.views.static import serve
from django.conf import settings
import hexoweb.pub as pub
from django.views.generic import TemplateView

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT},
            name='static'),

    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    path('login/', login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("init/", init_view, name="init"),
    path("update/", update_view, name="update"),
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
    path('api/set_s3/', set_s3, name='set_s3'),
    path('api/set_apikey/', set_api_key, name='set_apikey'),
    path('api/set_abbrlink/', set_abbrlink, name='set_abbrlink'),
    path('api/set_cust/', set_cust, name='set_cust'),
    path('api/set_value/', set_value, name='set_value'),
    path('api/del_value/', del_value, name='del_value'),
    path('api/new_value/', new_value, name='new_value'),
    path('api/add_friend/', add_friend, name='add_friend'),
    path('api/del_friend/', del_friend, name='del_friend'),
    path('api/edit_friend/', edit_friend, name='edit_friend'),
    path('api/fix/', auto_fix, name='auto_fix'),
    path('api/purge/', purge, name='purge'),
    path('api/webhook/', webhook, name='webhook'),
    path('api/create_webhook/', create_webhook_config, name='create_webhook'),
    path('api/get_update/', get_update, name='get_update'),
    path('api/do_update/', do_update, name='do_update'),

    path('pub/save/', pub.save, name='pub_save'),
    path('pub/save_post/', pub.save_post, name='pub_save_post'),
    path('pub/save_draft/', pub.save_draft, name='pub_save_draft'),
    path('pub/new/', pub.new, name='pub_new'),
    path('pub/delete/', pub.delete, name='pub_delete'),
    path('pub/delete_post/', pub.delete_post, name='pub_delete_post'),
    path('pub/create_webhook/', pub.create_webhook_config, name='pub_create_webhook'),
    path('pub/upload/', pub.upload_img, name='pub_upload'),
    path('pub/get_update/', pub.get_update, name='pub_get_update'),
    path('pub/get_posts/', pub.get_posts, name='pub_get_posts'),
    path('pub/get_pages/', pub.get_pages, name='pub_get_pages'),
    path('pub/get_configs/', pub.get_configs, name='pub_get_configs'),
    path('pub/get_images/', pub.get_images, name='pub_get_images'),
    path('pub/fix/', pub.auto_fix, name='pub_auto_fix'),
    path('pub/friends/', pub.friends, name='pub_friends'),

    re_path(r'^(?!api)^(?!pub).*$\.*', pages, name='pages'),
]

handler404 = page_404
handler500 = page_500
