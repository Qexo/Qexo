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
    path('api/set_api/', set_api, name='set_api'),
    path('api/set_abbrlink/', set_abbrlink, name='set_abbrlink'),
    path('api/set_cust/', set_cust, name='set_cust'),
    path('api/set_statistic/', set_statistic, name='set_statistic'),
    path('api/set_value/', set_value, name='set_value'),
    path('api/del_value/', del_value, name='del_value'),
    path('api/new_value/', new_value, name='new_value'),
    path('api/add_friend/', add_friend, name='add_friend'),
    path('api/del_friend/', del_friend, name='del_friend'),
    path('api/edit_friend/', edit_friend, name='edit_friend'),
    path('api/clean_friend/', clean_friend, name='clean_friend'),
    path('api/set_custom/', set_custom, name='set_custom'),
    path('api/del_custom/', del_custom, name='del_custom'),
    path('api/new_custom/', new_custom, name='new_custom'),
    path('api/fix/', auto_fix, name='auto_fix'),
    path('api/purge/', purge, name='purge'),
    path('api/webhook/', webhook, name='webhook'),
    path('api/create_webhook/', create_webhook_config, name='create_webhook'),
    path('api/do_update/', do_update, name='do_update'),
    path('api/get_notifications/', get_notifications, name='get_notifications'),
    path('api/del_notifications/', del_notification, name='del_notifications'),
    path('api/clear_notifications/', clear_notification, name='clear_notifications'),
    path('api/set_onepush/', set_onepush, name='set_onepush'),
    path('api/test_onepush/', test_onepush, name='test_onepush'),

    path('pub/save/', pub.save, name='pub_save'),
    path('pub/save_post/', pub.save_post, name='pub_save_post'),
    path('pub/save_draft/', pub.save_draft, name='pub_save_draft'),
    path('pub/new/', pub.new, name='pub_new'),
    path('pub/delete/', pub.delete, name='pub_delete'),
    path('pub/delete_post/', pub.delete_post, name='pub_delete_post'),
    path('pub/create_webhook/', pub.create_webhook_config, name='pub_create_webhook'),
    path('pub/get_posts/', pub.get_posts, name='pub_get_posts'),
    path('pub/get_pages/', pub.get_pages, name='pub_get_pages'),
    path('pub/get_configs/', pub.get_configs, name='pub_get_configs'),
    path('pub/get_images/', pub.get_images, name='pub_get_images'),
    path('pub/fix/', pub.auto_fix, name='pub_auto_fix'),
    path('pub/friends/', pub.friends, name='pub_friends'),
    path('pub/ask_friend/', pub.ask_friend, name='pub_ask_friend'),
    path('pub/add_friend/', pub.add_friend, name='pub_add_friend'),
    path('pub/edit_friend/', pub.edit_friend, name='pub_edit_friend'),
    path('pub/del_friend/', pub.del_friend, name='pub_del_friend'),
    path('pub/get_custom/', pub.get_custom, name='pub_get_custom'),
    path('pub/get_notifications/', pub.get_notifications, name='pub_get_notifications'),
    path('pub/status/', pub.status, name='pub_status'),
    path('pub/statistic/', pub.statistic, name='pub_statistic'),

    re_path(r'^(?!api)^(?!pub).*$\.*', pages, name='pages'),
]

handler404 = page_404
handler500 = page_500
handler403 = page_403
