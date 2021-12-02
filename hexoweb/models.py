from django.db import models
import uuid


class Cache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=0x7FFFFFFF)
    content = models.CharField(max_length=0x7FFFFFFF, blank=True)


class SettingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=0x7FFFFFFF)
    content = models.CharField(max_length=0x7FFFFFFF, blank=True)


class ImageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=0x7FFFFFFF)
    url = models.CharField(max_length=0x7FFFFFFF)
    size = models.CharField(max_length=0x7FFFFFFF)
    date = models.CharField(max_length=0x7FFFFFFF)
    type = models.CharField(max_length=0x7FFFFFFF)
