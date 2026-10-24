import json
import uuid

from django.test import TestCase

from hexoweb.models import (
    Cache,
    SettingModel,
    ImageModel,
    FriendModel,
    NotificationModel,
    CustomModel,
    PostModel,
    TalkModel,
    StatisticUV,
    StatisticPV,
)


class CacheModelTests(TestCase):
    """Cache 模型测试"""

    def setUp(self):
        self.cache_name = "test_cache"
        self.cache_content = "test content"

    def test_create_cache(self):
        """测试创建 Cache 对象"""
        cache = Cache.objects.create(name=self.cache_name, content=self.cache_content)
        self.assertEqual(cache.name, self.cache_name)
        self.assertEqual(cache.content, self.cache_content)
        self.assertIsInstance(cache.id, uuid.UUID)

    def test_cache_get_by_name_or_none_exists(self):
        """测试获取存在的 Cache 对象"""
        Cache.objects.create(name=self.cache_name, content=self.cache_content)
        cache = Cache.objects.get_by_name_or_none(self.cache_name)
        self.assertIsNotNone(cache)
        self.assertEqual(cache.name, self.cache_name)

    def test_cache_get_by_name_or_none_not_exists(self):
        """测试获取不存在的 Cache 对象返回 None"""
        cache = Cache.objects.get_by_name_or_none("non_existent")
        self.assertIsNone(cache)

    def test_cache_get_content_by_name_exists(self):
        """测试获取存在的 Cache 内容"""
        Cache.objects.create(name=self.cache_name, content=self.cache_content)
        content = Cache.objects.get_content_by_name(self.cache_name)
        self.assertEqual(content, self.cache_content)

    def test_cache_get_content_by_name_not_exists_default(self):
        """测试获取不存在的 Cache 内容返回默认值"""
        default = "default_value"
        content = Cache.objects.get_content_by_name("non_existent", default)
        self.assertEqual(content, default)

    def test_cache_exists_by_name_true(self):
        """测试检查存在的 Cache"""
        Cache.objects.create(name=self.cache_name, content=self.cache_content)
        exists = Cache.objects.exists_by_name(self.cache_name)
        self.assertTrue(exists)

    def test_cache_exists_by_name_false(self):
        """测试检查不存在的 Cache"""
        exists = Cache.objects.exists_by_name("non_existent")
        self.assertFalse(exists)


class SettingModelTests(TestCase):
    """SettingModel 模型测试"""

    def setUp(self):
        self.setting_name = "TEST_SETTING"
        self.setting_content = "test_value"

    def test_create_setting(self):
        """测试创建 Setting 对象"""
        setting = SettingModel.objects.create(name=self.setting_name, content=self.setting_content)
        self.assertEqual(setting.name, self.setting_name)
        self.assertEqual(setting.content, self.setting_content)

    def test_setting_get_by_name_or_none(self):
        """测试通过名称获取 Setting"""
        SettingModel.objects.create(name=self.setting_name, content=self.setting_content)
        setting = SettingModel.objects.get_by_name_or_none(self.setting_name)
        self.assertIsNotNone(setting)
        self.assertEqual(setting.content, self.setting_content)

    def test_setting_get_content_by_name_with_default(self):
        """测试获取 Setting 内容，不存在时使用默认值"""
        default_content = "default_setting_value"
        content = SettingModel.objects.get_content_by_name("NONEXISTENT_SETTING", default_content)
        self.assertEqual(content, default_content)


class ImageModelTests(TestCase):
    """ImageModel 模型测试"""

    def setUp(self):
        self.image_data = {
            "name": "test_image.jpg",
            "url": "https://example.com/image.jpg",
            "size": "1024KB",
            "date": "2025-01-01",
            "type": "jpg",
            "deleteConfig": '{"provider": "aliyun"}'
        }

    def test_create_image(self):
        """测试创建 Image 对象"""
        image = ImageModel.objects.create(**self.image_data)
        self.assertEqual(image.name, self.image_data["name"])
        self.assertEqual(image.url, self.image_data["url"])

    def test_image_default_delete_config(self):
        """测试 Image deleteConfig 默认值"""
        image = ImageModel.objects.create(
            name="test.jpg",
            url="https://example.com/test.jpg",
            size="512KB",
            date="2025-01-01",
            type="jpg"
        )
        self.assertEqual(image.deleteConfig, "{}")


class FriendModelTests(TestCase):
    """FriendModel 模型测试"""

    def test_create_friend(self):
        """测试创建 Friend 对象"""
        friend = FriendModel.objects.create(
            name="Test Friend",
            url="https://example.com",
            imageUrl="https://example.com/avatar.jpg",
            time="2025-01-01",
            description="A test friend",
            status=True
        )
        self.assertEqual(friend.name, "Test Friend")
        self.assertTrue(friend.status)

    def test_friend_default_status(self):
        """测试 Friend 默认状态为 True"""
        friend = FriendModel.objects.create(
            name="Test Friend",
            url="https://example.com",
            imageUrl="https://example.com/default-avatar.jpg",
            time="2025-01-01",
            description="Default friend description"
        )
        self.assertTrue(friend.status)


class PostModelTests(TestCase):
    """PostModel 模型测试"""

    def test_create_post(self):
        """测试创建 Post 对象"""
        post = PostModel.objects.create(
            title="Test Post",
            filename="test-post.md",
            path="/posts/test-post",
            date=1622505600.0,
            status=True
        )
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.path, "/posts/test-post")
        self.assertTrue(post.status)

    def test_post_front_matter_default(self):
        """测试 Post front_matter 默认值"""
        post = PostModel.objects.create(
            title="Test Post",
            filename="test.md",
            path="/posts/test",
            date=1622505600.0
        )
        self.assertEqual(post.front_matter, "{}")

    def test_post_by_path_index(self):
        """测试 Post 的 path 索引"""
        PostModel.objects.create(
            title="Post 1",
            filename="post1.md",
            path="/posts/post1",
            date=1622505600.0
        )
        posts = PostModel.objects.filter(path="/posts/post1")
        self.assertEqual(posts.count(), 1)


class TalkModelTests(TestCase):
    """TalkModel 模型测试"""

    def test_create_talk(self):
        """测试创建 Talk 对象"""
        talk = TalkModel.objects.create(
            content="Test talk content",
            tags="tag1,tag2",
            time="2025-01-01T12:00:00"
        )
        self.assertEqual(talk.content, "Test talk content")
        self.assertEqual(talk.tags, "tag1,tag2")

    def test_talk_like_default(self):
        """测试 Talk like 默认值"""
        talk = TalkModel.objects.create(
            content="Test",
            time="2025-01-01"
        )
        self.assertEqual(talk.like, "[]")

    def test_talk_values_default(self):
        """测试 Talk values 默认值"""
        talk = TalkModel.objects.create(
            content="Test",
            time="2025-01-01"
        )
        self.assertEqual(talk.values, "{}")


class StatisticTests(TestCase):
    """统计模型测试"""

    def test_create_uv_statistic(self):
        """测试创建 UV 统计"""
        stat = StatisticUV.objects.create(ip="192.168.1.1")
        self.assertEqual(stat.ip, "192.168.1.1")

    def test_create_pv_statistic(self):
        """测试创建 PV 统计"""
        stat = StatisticPV.objects.create(
            url="https://example.com/page",
            number=10
        )
        self.assertEqual(stat.url, "https://example.com/page")
        self.assertEqual(stat.number, 10)


class ModelFieldValidationTests(TestCase):
    """模型字段验证和约束测试"""

    def test_cache_empty_name_allowed(self):
        """测试 Cache 空名称是否被允许"""
        cache = Cache.objects.create(name="", content="test")
        self.assertEqual(cache.name, "")

    def test_cache_very_long_content(self):
        """测试 Cache 长内容处理"""
        long_content = "x" * 10000
        cache = Cache.objects.create(name="long_cache", content=long_content)
        self.assertEqual(len(cache.content), 10000)

    def test_setting_model_unicode_content(self):
        """测试 Setting 模型 Unicode 内容"""
        setting = SettingModel.objects.create(
            name="UNICODE_TEST",
            content="测试 📝 Тест 🎉"
        )
        retrieved = SettingModel.objects.get(name="UNICODE_TEST")
        self.assertEqual(retrieved.content, "测试 📝 Тест 🎉")

    def test_image_model_url_field(self):
        """测试 Image 模型 URL 字段"""
        image = ImageModel.objects.create(
            name="image.png",
            url="https://cdn.example.com/images/test.png?v=1&format=webp",
            size="2MB",
            date="2025-01-01",
            type="png"
        )
        self.assertTrue(image.url.startswith("https://"))

    def test_friend_model_with_special_characters_in_name(self):
        """测试 Friend 模型名称中包含特殊字符"""
        friend = FriendModel.objects.create(
            name="Friend & Co. #1",
            url="https://example.com",
            imageUrl="https://example.com/friend-special.jpg",
            time="2025-01-01",
            description="Friend with special chars"
        )
        self.assertIn("&", friend.name)

    def test_post_model_with_long_title(self):
        """测试 Post 模型长标题"""
        long_title = "A" * 255
        post = PostModel.objects.create(
            title=long_title,
            filename="test.md",
            path="/posts/test",
            date=1622505600.0
        )
        self.assertEqual(len(post.title), 255)

    def test_talk_model_with_empty_tags(self):
        """测试 Talk 模型空标签"""
        talk = TalkModel.objects.create(
            content="Test",
            tags="",
            time="2025-01-01"
        )
        self.assertEqual(talk.tags, "")

    def test_talk_model_with_json_values(self):
        """测试 Talk 模型 JSON 字段"""

        talk = TalkModel.objects.create(
            content="Test",
            time="2025-01-01",
            values='{"key": "value", "count": 42}'
        )
        data = json.loads(talk.values)
        self.assertEqual(data["count"], 42)


class NotificationModelTests(TestCase):
    """NotificationModel 模型测试"""

    def test_create_notification(self):
        """测试创建通知"""
        notification = NotificationModel.objects.create(
            label="Test Notification",
            content="Notification content",
            time="2025-01-01"
        )
        self.assertEqual(notification.label, "Test Notification")
        self.assertEqual(notification.content, "Notification content")

    def test_notification_str_representation(self):
        """测试通知对象字符串表示"""
        notification = NotificationModel.objects.create(
            label="Test",
            content="Content",
            time="2025-01-01"
        )
        self.assertIsNotNone(str(notification))

    def test_bulk_notification_creation(self):
        """测试批量创建通知"""
        notifications = [
            NotificationModel(label=f"notif_{i}", content=f"content_{i}", time="2025-01-01")
            for i in range(5)
        ]
        NotificationModel.objects.bulk_create(notifications)
        self.assertEqual(NotificationModel.objects.count(), 5)


class CustomModelTests(TestCase):
    """CustomModel 模型测试"""

    def test_create_custom_model(self):
        """测试创建 CustomModel"""
        custom = CustomModel.objects.create(
            name="Custom Item",
            content="Custom content"
        )
        self.assertEqual(custom.name, "Custom Item")

    def test_custom_model_query_by_name(self):
        """测试 CustomModel 按名称查询"""
        CustomModel.objects.create(name="Item1", content="Content1")
        CustomModel.objects.create(name="Item2", content="Content2")

        item = CustomModel.objects.filter(name="Item1").first()
        self.assertIsNotNone(item)
        self.assertEqual(item.content, "Content1")

    def test_custom_model_update(self):
        """测试更新 CustomModel"""
        custom = CustomModel.objects.create(name="Original", content="Original")
        custom.content = "Updated"
        custom.save()

        updated = CustomModel.objects.get(id=custom.id)
        self.assertEqual(updated.content, "Updated")


class ModelSerializationTests(TestCase):
    """模型序列化和表示测试"""

    def test_cache_model_str_method(self):
        """测试 Cache __str__ 方法"""
        cache = Cache.objects.create(name="test_cache", content="content")
        str_repr = str(cache)
        self.assertIsNotNone(str_repr)

    def test_setting_model_str_method(self):
        """测试 Setting __str__ 方法"""
        setting = SettingModel.objects.create(name="TEST", content="value")
        str_repr = str(setting)
        self.assertIsNotNone(str_repr)

    def test_post_model_repr(self):
        """测试 Post 模型表示"""
        post = PostModel.objects.create(
            title="Test Post",
            filename="test.md",
            path="/test",
            date=1622505600.0
        )
        self.assertIsNotNone(repr(post))

    def test_json_field_serialization(self):
        """测试 JSON 字段序列化"""

        post = PostModel.objects.create(
            title="JSON Test",
            filename="test.md",
            path="/test",
            date=1622505600.0,
            front_matter='{"key": "value"}'
        )

        data = json.loads(post.front_matter)
        self.assertEqual(data["key"], "value")
