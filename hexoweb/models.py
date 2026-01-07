from django.db import models
import uuid


class Cache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF, db_index=True)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class SettingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF, db_index=True)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class ImageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF, db_index=True)
    url = models.TextField(max_length=0x7FFFFFFF)
    size = models.TextField(max_length=0x7FFFFFFF)
    date = models.TextField(max_length=0x7FFFFFFF)
    type = models.TextField(max_length=0x7FFFFFFF)
    deleteConfig = models.TextField(max_length=0x7FFFFFFF, default="{}")

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-date']),  # 倒序索引，常用于按时间倒序查询
        ]


class FriendModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF, blank=False)
    url = models.TextField(max_length=0x7FFFFFFF, blank=False)
    imageUrl = models.TextField(max_length=0x7FFFFFFF)
    time = models.TextField(max_length=0x7FFFFFFF, blank=False, db_index=True)
    description = models.TextField(max_length=0x7FFFFFFF)
    status = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['time']),
            models.Index(fields=['status']),
        ]


class NotificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.TextField(max_length=0x7FFFFFFF)
    label = models.TextField(max_length=0x7FFFFFFF, blank=True)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)


class CustomModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=0x7FFFFFFF, db_index=True)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class StatisticUV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip = models.GenericIPAddressField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['ip']),
        ]


class StatisticPV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(db_index=True)
    number = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['url']),
        ]


class TalkModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(max_length=0x7FFFFFFF, blank=True)
    tags = models.TextField(max_length=0x7FFFFFFF, blank=True)
    time = models.TextField(max_length=0x7FFFFFFF, db_index=True)
    like = models.TextField(max_length=0x7FFFFFFF, blank=True, default="[]")
    values = models.TextField(max_length=0x7FFFFFFF, default="{}")

    class Meta:
        indexes = [
            models.Index(fields=['time']),
            models.Index(fields=['-time']),  # 倒序索引
        ]


class PostModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(max_length=0x7FFFFFFF, blank=False)
    filename = models.TextField(max_length=0x7FFFFFFF, blank=False)
    path = models.TextField(max_length=0x7FFFFFFF, blank=False, db_index=True)
    date = models.FloatField(db_index=True)
    front_matter = models.TextField(max_length=0x7FFFFFFF, blank=True, default="{}")
    status = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['path']),
            models.Index(fields=['-date']),  # 倒序索引，用于按日期倒序查询
            models.Index(fields=['status']),
        ]
