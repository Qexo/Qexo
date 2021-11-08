from django.contrib import admin
from .models import Cache, SettingModel, ImageModel


class CacheAdmin(admin.ModelAdmin):
    list_display = ['name']


class SettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'content']

class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'size', 'date']


admin.site.register(Cache, CacheAdmin)
admin.site.register(ImageModel, ImageAdmin)
admin.site.register(SettingModel, SettingAdmin)
