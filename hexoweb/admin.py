from django.contrib import admin
from .models import Cache, SettingModel, ImageModel, StatisticPV, StatisticUV


class CacheAdmin(admin.ModelAdmin):
    list_display = ['name']


class SettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'content']


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'size', 'date']


class StatisticUVAdmin(admin.ModelAdmin):
    list_display = ['ip']


class StatisticPVAdmin(admin.ModelAdmin):
    list_display = ['url', 'number']


admin.site.register(Cache, CacheAdmin)
admin.site.register(ImageModel, ImageAdmin)
admin.site.register(SettingModel, SettingAdmin)
admin.site.register(StatisticUV, StatisticUVAdmin)
admin.site.register(StatisticPV, StatisticPVAdmin)
