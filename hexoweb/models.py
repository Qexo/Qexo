from django.db import models
import uuid


class NameBasedQuerySet(models.QuerySet):
    """基于name字段的通用QuerySet，提供便捷查询方法"""
    
    def get_by_name_or_none(self, name):
        """
        通过name获取对象，不存在返回None而非抛出异常
        
        Args:
            name: 要查询的name值
            
        Returns:
            对象实例或None
            
        Example:
            obj = SettingModel.objects.get_by_name_or_none("CDN_PREV")
        """
        try:
            return self.get(name=name)
        except self.model.DoesNotExist:
            return None
    
    def get_content_by_name(self, name, default=""):
        """
        获取name字段对应的content，不存在返回默认值
        
        Args:
            name: 要查询的name值
            default: 默认值，当对象不存在时返回
            
        Returns:
            content字符串或默认值
            
        Example:
            cdn = SettingModel.objects.get_content_by_name("CDN_PREV", "https://cdn.default.com")
        """
        obj = self.get_by_name_or_none(name)
        return obj.content if obj else default
    
    def exists_by_name(self, name):
        """
        高效检查name是否存在（比count()快，不需要计数只需判断存在）
        
        Args:
            name: 要检查的name值
            
        Returns:
            布尔值
            
        Example:
            if SettingModel.objects.exists_by_name("CDN_PREV"):
                ...
        """
        return self.filter(name=name).exists()


class NameBasedManager(models.Manager):
    """使用NameBasedQuerySet的Manager"""
    def get_queryset(self):
        return NameBasedQuerySet(self.model, using=self._db)
    
    def get_by_name_or_none(self, name):
        return self.get_queryset().get_by_name_or_none(name)
    
    def get_content_by_name(self, name, default=""):
        return self.get_queryset().get_content_by_name(name, default)
    
    def exists_by_name(self, name):
        return self.get_queryset().exists_by_name(name)


class Cache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    content = models.TextField(blank=True)

    objects = NameBasedManager()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class SettingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    content = models.TextField(blank=True)

    objects = NameBasedManager()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class ImageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    url = models.TextField()
    size = models.TextField()
    date = models.TextField()
    type = models.TextField()
    deleteConfig = models.TextField(default="{}")

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-date']),  # 倒序索引，常用于按时间倒序查询
        ]


class FriendModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(blank=False)
    url = models.TextField(blank=False)
    imageUrl = models.TextField()
    time = models.TextField(blank=False, db_index=True)
    description = models.TextField()
    status = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['time']),
            models.Index(fields=['status']),
        ]


class NotificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.TextField()
    label = models.TextField(blank=True)
    content = models.TextField(blank=True)


class CustomModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    content = models.TextField(blank=True)

    objects = NameBasedManager()

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
    content = models.TextField(blank=True)
    tags = models.TextField(blank=True)
    time = models.TextField(db_index=True)
    like = models.TextField(blank=True, default="[]")
    values = models.TextField(default="{}")

    class Meta:
        indexes = [
            models.Index(fields=['time']),
            models.Index(fields=['-time']),  # 倒序索引
        ]


class PostModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(blank=False)
    filename = models.TextField(blank=False)
    path = models.TextField(blank=False, db_index=True)
    date = models.FloatField(db_index=True)
    front_matter = models.TextField(blank=True, default="{}")
    status = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['path']),
            models.Index(fields=['-date']),  # 倒序索引，用于按日期倒序查询
            models.Index(fields=['status']),
        ]
