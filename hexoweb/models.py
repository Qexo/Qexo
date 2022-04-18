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


class FriendModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=0x7FFFFFFF, blank=False)
    url = models.CharField(max_length=0x7FFFFFFF, blank=False)
    imageUrl = models.CharField(max_length=0x7FFFFFFF)
    time = models.CharField(max_length=0x7FFFFFFF, blank=False)
    description = models.CharField(max_length=0x7FFFFFFF)
    status = models.BooleanField(default=True)


class NotificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.CharField(max_length=0x7FFFFFFF)
    label = models.CharField(max_length=0x7FFFFFFF, blank=True)
    content = models.CharField(max_length=0x7FFFFFFF, blank=True)


class CustomModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=0x7FFFFFFF)
    content = models.CharField(max_length=0x7FFFFFFF, blank=True)


class StatisticUV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip = models.GenericIPAddressField()


class StatisticPV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    number = models.IntegerField(default=0)
