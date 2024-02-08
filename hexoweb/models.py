from django.db import models
import uuid


class Cache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)


class SettingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)


class ImageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF)
    url = models.TextField(max_length=0x7FFFFFFF)
    size = models.TextField(max_length=0x7FFFFFFF)
    date = models.TextField(max_length=0x7FFFFFFF)
    type = models.TextField(max_length=0x7FFFFFFF)
    deleteConfig = models.TextField(max_length=0x7FFFFFFF, default="{}")


class FriendModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF, blank=False)
    url = models.TextField(max_length=0x7FFFFFFF, blank=False)
    imageUrl = models.TextField(max_length=0x7FFFFFFF)
    time = models.TextField(max_length=0x7FFFFFFF, blank=False)
    description = models.TextField(max_length=0x7FFFFFFF)
    status = models.BooleanField(default=True)


class NotificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.TextField(max_length=0x7FFFFFFF)
    label = models.TextField(max_length=0x7FFFFFFF, blank=True)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)


class CustomModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)


class StatisticUV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip = models.GenericIPAddressField()


class StatisticPV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    number = models.IntegerField(default=0)


class TalkModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)
    tags = models.TextField(max_length=0x7FFFFFFF, blank=True)
    time = models.TextField(max_length=0x7FFFFFFF)
    like = models.TextField(max_length=0x7FFFFFFF, blank=True, default="[]")
    values = models.TextField(max_length=0x7FFFFFFF, default="{}")


class PostModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(max_length=0x7FFFFFFF, blank=False)
    filename = models.TextField(max_length=0x7FFFFFFF, blank=False)
    path = models.TextField(max_length=0x7FFFFFFF, blank=False)
    date = models.FloatField()
    front_matter = models.TextField(max_length=0x7FFFFFFF, blank=True, default="{}")
    status = models.BooleanField(default=True)
