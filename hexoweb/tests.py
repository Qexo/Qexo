from django.core.management import call_command
from django.db import connection, IntegrityError
from django.test import SimpleTestCase, TransactionTestCase, TestCase, Client
from django.urls import resolve, reverse
from django.contrib.auth.models import User
import json
import uuid

from hexoweb.models import (
    Cache, SettingModel, ImageModel, FriendModel, 
    NotificationModel, CustomModel, PostModel, TalkModel,
    StatisticUV, StatisticPV
)


# ===== URL 烟雾测试 =====
class UrlSmokeTests(SimpleTestCase):
    def test_home_url(self):
        self.assertEqual(reverse("home"), "/")

    def test_login_url(self):
        self.assertEqual(reverse("login"), "/login/")

    def test_api_auth_url_resolves(self):
        self.assertEqual(resolve("/api/auth/").view_name, "auth")


# ===== 数据库迁移测试 =====
class SQLiteMigrationSmokeTests(TransactionTestCase):
    databases = {"default"}

    def test_default_sqlite_database_can_run_migrate(self):
        self.assertEqual(connection.vendor, "sqlite")
        call_command("migrate", database="default", interactive=False, verbosity=0)
        self.assertIn("django_migrations", connection.introspection.table_names())


# ===== 模型测试 =====
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


# ===== API 端点测试 =====
class AuthApiTests(TestCase):
    """认证 API 测试"""
    
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        self.user.is_staff = True
        self.user.save()
    
    def test_auth_endpoint_exists(self):
        """测试 /api/auth/ 端点存在"""
        response = self.client.post("/api/auth/", {})
        # 端点应该存在（不返回 404）
        self.assertNotEqual(response.status_code, 404)
    
    def test_auth_returns_json(self):
        """测试认证端点返回 JSON"""
        response = self.client.post("/api/auth/", {
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_auth_response_has_required_fields(self):
        """测试认证响应包含必需字段"""
        response = self.client.post("/api/auth/", {
            "username": self.username,
            "password": self.password
        })
        data = json.loads(response.content)
        self.assertIn("status", data)
        self.assertIn("msg", data)


# ===== 视图测试 =====
class ViewsTests(TestCase):
    """视图函数测试"""
    
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        self.user.is_staff = True
        self.user.save()
    
    def test_login_view_redirects_authenticated_user(self):
        """测试已认证用户访问登录页面重定向"""
        # Use Django's test client authentication instead of client.login()
        # due to passkeys backend requiring a request object
        self.client.force_login(self.user)
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 302)
    
    def test_login_view_accessible_for_anonymous(self):
        """测试匿名用户可以访问登录页面"""
        response = self.client.get('/login/')
        # 在部分配置下会渲染登录页，在初始化流程下会重定向
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            self.assertTrue(response.url.startswith("/init/"))
    
    def test_home_view_accessible(self):
        """测试首页可以访问"""
        response = self.client.get('/')
        # 首页应该返回 200 或重定向到登录页
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            self.assertTrue(
                response.url.startswith("/login/?next=") or response.url.startswith("/init/")
            )


class MigrateViewDataSafetyTests(TestCase):
    """迁移导入导出安全性回归测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="migrate_user", password="migrate_pass")
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)

    def test_export_contains_talk_values_field(self):
        """导出说说时应包含 values 字段，避免数据丢失"""
        TalkModel.objects.create(
            content="hello",
            tags="test",
            time="2026-01-01T00:00:00",
            like='["u1"]',
            values='{"liked_users": ["u1"]}'
        )

        response = self.client.post('/migrate/', {"type": "export"})
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode("utf-8"))
        self.assertIn("talks", payload)
        self.assertEqual(len(payload["talks"]), 1)
        self.assertIn("values", payload["talks"][0])
        self.assertEqual(payload["talks"][0]["values"], '{"liked_users": ["u1"]}')

    def test_import_posts_failure_does_not_delete_existing_data(self):
        """导入失败时应回滚，保留旧数据"""
        PostModel.objects.create(
            title="old",
            filename="old.md",
            path="/old",
            date=1622505600.0,
            front_matter="{}",
            status=True
        )

        response = self.client.post('/migrate/', {
            "type": "import_posts",
            "data": json.dumps({"not": "a list"})
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PostModel.objects.filter(path="/old").count(), 1)
        self.assertEqual(PostModel.objects.count(), 1)

    def test_import_posts_legacy_data_without_filename(self):
        """兼容旧备份：缺失 filename 时应可导入"""
        legacy_posts = [{
            "title": "legacy",
            "path": "/legacy",
            "status": True,
            "front_matter": "{}",
            "date": 1622505600.0
        }]

        response = self.client.post('/migrate/', {
            "type": "import_posts",
            "data": json.dumps(legacy_posts)
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostModel.objects.count(), 1)
        post = PostModel.objects.first()
        self.assertIsNotNone(post)
        self.assertEqual(post.path, "/legacy")
        self.assertEqual(post.filename, "/legacy")


# ===== 查询和性能测试 =====
class QueryPerformanceTests(TestCase):
    """查询性能和优化测试"""
    
    def test_cache_query_with_index(self):
        """测试带索引的查询性能"""
        for i in range(10):
            Cache.objects.create(name=f"cache_{i}", content=f"content_{i}")
        
        # 使用索引字段查询应该很快
        cache = Cache.objects.filter(name="cache_5").first()
        self.assertIsNotNone(cache)
    
    def test_bulk_create_performance(self):
        """测试批量创建性能"""
        caches = [
            Cache(name=f"bulk_cache_{i}", content=f"content_{i}")
            for i in range(100)
        ]
        Cache.objects.bulk_create(caches)
        self.assertEqual(Cache.objects.filter(name__startswith="bulk_cache").count(), 100)
    
    def test_setting_queryset_efficiency(self):
        """测试 Setting QuerySet 效率"""
        SettingModel.objects.create(name="SETTING1", content="value1")
        SettingModel.objects.create(name="SETTING2", content="value2")
        
        # 测试自定义管理器方法
        setting = SettingModel.objects.get_by_name_or_none("SETTING1")
        self.assertIsNotNone(setting)
        
        non_existent = SettingModel.objects.get_by_name_or_none("NONEXISTENT")
        self.assertIsNone(non_existent)


# ===== 模型字段和验证测试 =====
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


# ===== NotificationModel 和 CustomModel 测试 =====
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


# ===== 高级查询测试 =====
class AdvancedQueryTests(TestCase):
    """高级查询和过滤测试"""
    
    def test_cache_filter_by_name_pattern(self):
        """测试按名称模式过滤 Cache"""
        Cache.objects.create(name="prod_cache_1", content="prod1")
        Cache.objects.create(name="prod_cache_2", content="prod2")
        Cache.objects.create(name="test_cache_1", content="test1")
        
        prod_caches = Cache.objects.filter(name__startswith="prod_cache")
        self.assertEqual(prod_caches.count(), 2)
    
    def test_post_filter_by_status(self):
        """测试按状态过滤 Post"""
        PostModel.objects.create(
            title="Published", filename="pub.md", path="/pub",
            date=1622505600.0, status=True
        )
        PostModel.objects.create(
            title="Draft", filename="draft.md", path="/draft",
            date=1622505600.0, status=False
        )
        
        published = PostModel.objects.filter(status=True)
        self.assertEqual(published.count(), 1)
    
    def test_friend_filter_by_status_and_query_count(self):
        """测试按状态过滤 Friend 并计数"""
        for i in range(3):
            FriendModel.objects.create(
                name=f"Friend{i}",
                url=f"https://example{i}.com",
                imageUrl=f"https://example{i}.com/avatar.jpg",
                time="2025-01-01",
                description=f"Friend {i} description",
                status=True
            )
        
        active_friends = FriendModel.objects.filter(status=True)
        self.assertEqual(active_friends.count(), 3)
    
    def test_image_filter_by_type(self):
        """测试按类型过滤 Image"""
        ImageModel.objects.create(name="img1.jpg", url="http://ex.com/1", size="100KB", date="2025-01-01", type="jpg")
        ImageModel.objects.create(name="img2.png", url="http://ex.com/2", size="120KB", date="2025-01-01", type="png")
        ImageModel.objects.create(name="img3.jpg", url="http://ex.com/3", size="110KB", date="2025-01-01", type="jpg")
        
        jpg_images = ImageModel.objects.filter(type="jpg")
        self.assertEqual(jpg_images.count(), 2)


# ===== 模型关系和依赖测试 =====
class ModelDeletionTests(TestCase):
    """模型删除和级联测试"""
    
    def test_cache_deletion(self):
        """测试删除 Cache"""
        cache = Cache.objects.create(name="to_delete", content="content")
        cache_id = cache.id
        cache.delete()
        
        self.assertFalse(Cache.objects.filter(id=cache_id).exists())
    
    def test_setting_deletion(self):
        """测试删除 Setting"""
        setting = SettingModel.objects.create(name="TEMP", content="temp")
        setting.delete()
        
        self.assertFalse(SettingModel.objects.filter(name="TEMP").exists())
    
    def test_bulk_delete_caches(self):
        """测试批量删除 Cache"""
        for i in range(5):
            Cache.objects.create(name=f"cache_{i}", content=f"content_{i}")
        
        Cache.objects.filter(name__startswith="cache_").delete()
        self.assertEqual(Cache.objects.filter(name__startswith="cache_").count(), 0)


# ===== 边界条件和异常测试 =====
class EdgeCaseTests(TestCase):
    """边界条件和异常处理测试"""
    
    def test_cache_with_null_content_rejected_by_db(self):
        """测试 Cache content 为 None 时会触发数据库 NOT NULL 约束"""
        cache = Cache(name="test", content=None)
        cache.full_clean()
        with self.assertRaises(IntegrityError):
            cache.save()
    
    def test_very_large_uuid_handling(self):
        """测试 UUID 字段处理"""
        cache = Cache.objects.create(name="uuid_test", content="test")
        self.assertIsInstance(cache.id, uuid.UUID)
    
    def test_duplicate_cache_names_allowed(self):
        """测试是否允许重复的 Cache 名称"""
        Cache.objects.create(name="duplicate", content="content1")
        Cache.objects.create(name="duplicate", content="content2")
        
        duplicates = Cache.objects.filter(name="duplicate")
        self.assertEqual(duplicates.count(), 2)
    
    def test_statistic_uv_duplicate_ip_handling(self):
        """测试统计中重复 IP 的处理"""
        StatisticUV.objects.create(ip="192.168.1.1")
        StatisticUV.objects.create(ip="192.168.1.1")
        
        # 测试是否允许重复
        count = StatisticUV.objects.filter(ip="192.168.1.1").count()
        self.assertEqual(count, 2)
    
    def test_post_date_as_float(self):
        """测试 Post 日期字段为浮点数"""
        post = PostModel.objects.create(
            title="Float Date Test",
            filename="test.md",
            path="/test",
            date=1622505600.123456
        )
        self.assertIsInstance(post.date, (int, float))


# ===== API 响应格式测试 =====
class ApiResponseTests(TestCase):
    """API 响应格式和内容测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="apiuser",
            password="apipass123"
        )
        self.user.is_staff = True
        self.user.save()
    
    def test_auth_api_response_structure(self):
        """测试认证 API 响应结构"""
        response = self.client.post("/api/auth/", {
            "username": "apiuser",
            "password": "apipass123"
        })
        
        try:
            data = json.loads(response.content)
            self.assertIn("status", data)
            self.assertIn("msg", data)
        except json.JSONDecodeError:
            self.fail("API 响应不是有效的 JSON")
    
    def test_api_response_is_json_format(self):
        """测试 API 返回 JSON 格式"""
        response = self.client.post("/api/auth/", {})
        self.assertEqual(
            response.get('Content-Type', ''),
            'application/json',
            "API 应该返回 JSON 格式"
        )
    
    def test_api_error_response_format(self):
        """测试 API 错误响应格式"""
        response = self.client.post("/api/auth/", {
            "username": "wronguser",
            "password": "wrongpass"
        })
        
        # 应该返回 JSON 格式的错误
        self.assertEqual(response['Content-Type'], 'application/json')


# ===== 数据库一致性测试 =====
class DatabaseConsistencyTests(TestCase):
    """数据库一致性和完整性测试"""
    
    def test_cache_unique_by_id_not_by_name(self):
        """测试 Cache 对象 ID 唯一性"""
        cache1 = Cache.objects.create(name="test", content="content1")
        cache2 = Cache.objects.create(name="test", content="content2")
        
        self.assertNotEqual(cache1.id, cache2.id)
    
    def test_post_multiple_with_same_title(self):
        """测试是否允许相同标题的 Post"""
        PostModel.objects.create(
            title="Same Title",
            filename="post1.md",
            path="/post1",
            date=1622505600.0
        )
        PostModel.objects.create(
            title="Same Title",
            filename="post2.md",
            path="/post2",
            date=1622505600.0
        )
        
        same_titles = PostModel.objects.filter(title="Same Title")
        self.assertEqual(same_titles.count(), 2)
    
    def test_friend_url_field_uniqueness_not_enforced(self):
        """测试 Friend URL 字段是否唯一"""
        FriendModel.objects.create(
            name="Friend1",
            url="https://example.com",
            imageUrl="https://example.com/friend1.jpg",
            time="2025-01-01",
            description="Friend 1"
        )
        FriendModel.objects.create(
            name="Friend2",
            url="https://example.com",
            imageUrl="https://example.com/friend2.jpg",
            time="2025-01-01",
            description="Friend 2"
        )
        
        same_url = FriendModel.objects.filter(url="https://example.com")
        self.assertEqual(same_url.count(), 2)
    
    def test_setting_name_uniqueness_or_not(self):
        """测试 Setting 名称允许重复（无唯一约束）"""
        SettingModel.objects.create(name="SETTING", content="value1")
        SettingModel.objects.create(name="SETTING", content="value2")
        count = SettingModel.objects.filter(name="SETTING").count()
        self.assertEqual(count, 2)


# ===== 模型表示和序列化测试 =====
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


# ===== 查询集操作测试 =====
class QuerySetOperationTests(TestCase):
    """QuerySet 操作测试"""
    
    def test_queryset_values_list(self):
        """测试 QuerySet values_list 操作"""
        Cache.objects.create(name="cache1", content="content1")
        Cache.objects.create(name="cache2", content="content2")
        
        names = Cache.objects.values_list("name", flat=True)
        self.assertIn("cache1", list(names))
    
    def test_queryset_exclude(self):
        """测试 QuerySet exclude 操作"""
        PostModel.objects.create(title="Pub", filename="pub.md", path="/pub", date=1622505600.0, status=True)
        PostModel.objects.create(title="Draft", filename="draft.md", path="/draft", date=1622505600.0, status=False)
        
        published = PostModel.objects.exclude(status=False)
        self.assertEqual(published.count(), 1)
    
    def test_queryset_ordering(self):
        """测试 QuerySet 排序"""
        PostModel.objects.create(title="Post1", filename="p1.md", path="/p1", date=1622505600.0)
        PostModel.objects.create(title="Post2", filename="p2.md", path="/p2", date=1622505601.0)
        
        ordered = PostModel.objects.order_by("-date")
        titles = [p.title for p in ordered]
        self.assertEqual(titles[0], "Post2")
    
    def test_queryset_distinct(self):
        """测试 QuerySet distinct 操作"""
        FriendModel.objects.create(
            name="Friend",
            url="https://ex.com",
            imageUrl="https://ex.com/friend.jpg",
            time="2025-01-01",
            description="Friend distinct 1",
            status=True
        )
        FriendModel.objects.create(
            name="Friend",
            url="https://ex.com",
            imageUrl="https://ex.com/friend2.jpg",
            time="2025-01-01",
            description="Friend distinct 2",
            status=True
        )
        
        distinct_friends = FriendModel.objects.values("name").distinct()
        self.assertEqual(distinct_friends.count(), 1)


# ===== 管理器方法测试 =====
class ManagerMethodTests(TestCase):
    """自定义管理器方法测试"""
    
    def test_cache_manager_get_by_name_or_none_returns_none_for_missing(self):
        """测试 Cache 管理器返回 None"""
        result = Cache.objects.get_by_name_or_none("nonexistent_12345")
        self.assertIsNone(result)
    
    def test_cache_manager_get_content_by_name_returns_content(self):
        """测试 Cache 管理器返回内容"""
        Cache.objects.create(name="content_test", content="my_content")
        result = Cache.objects.get_content_by_name("content_test")
        self.assertEqual(result, "my_content")
    
    def test_cache_manager_exists_by_name(self):
        """测试 Cache 管理器检查存在性"""
        Cache.objects.create(name="exists_test", content="content")
        
        exists = Cache.objects.exists_by_name("exists_test")
        self.assertTrue(exists)
        
        not_exists = Cache.objects.exists_by_name("nonexistent_test")
        self.assertFalse(not_exists)
    
    def test_setting_manager_get_by_name_or_none(self):
        """测试 Setting 管理器"""
        SettingModel.objects.create(name="TEST_SETTING", content="test_value")
        
        result = SettingModel.objects.get_by_name_or_none("TEST_SETTING")
        self.assertIsNotNone(result)
        self.assertEqual(result.content, "test_value")


# ===== 集成测试 =====
class IntegrationTests(TestCase):
    """集成测试 - 测试多个组件间的交互"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin",
            password="admin123"
        )
        self.user.is_staff = True
        self.user.save()
    
    def test_create_post_and_retrieve_by_path(self):
        """测试创建 Post 并通过路径检索"""
        post = PostModel.objects.create(
            title="Integration Test Post",
            filename="integration.md",
            path="/posts/integration",
            date=1622505600.0,
            status=True
        )
        
        retrieved = PostModel.objects.filter(path=post.path).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Integration Test Post")
    
    def test_create_cache_and_retrieve_by_name(self):
        """测试创建 Cache 并通过名称检索"""
        Cache.objects.create(name="integration_cache", content="test_content")
        
        retrieved = Cache.objects.get_by_name_or_none("integration_cache")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "test_content")
    
    def test_multiple_model_operations_in_sequence(self):
        """测试多个模型操作的序列"""
        # 创建 Cache
        cache = Cache.objects.create(name="seq_cache", content="content")
        
        # 创建 Setting
        setting = SettingModel.objects.create(name="SEQ_SETTING", content="value")
        
        # 创建 Post
        post = PostModel.objects.create(
            title="Seq Post",
            filename="seq.md",
            path="/seq",
            date=1622505600.0
        )
        
        # 验证所有对象都被创建
        self.assertIsNotNone(cache.id)
        self.assertIsNotNone(setting.id)
        self.assertIsNotNone(post.id)
        
        # 验证它们可以被独立检索
        self.assertIsNotNone(Cache.objects.get(id=cache.id))
        self.assertIsNotNone(SettingModel.objects.get(name="SEQ_SETTING"))
        self.assertIsNotNone(PostModel.objects.get(path="/seq"))


# ===== 数据批量操作测试 =====
class BulkOperationsTests(TestCase):
    """数据批量操作测试"""
    
    def test_bulk_create_multiple_posts(self):
        """测试批量创建 Posts"""
        posts = [
            PostModel(
                title=f"Bulk Post {i}",
                filename=f"bulk_{i}.md",
                path=f"/bulk/{i}",
                date=1622505600.0 + i,
                status=True
            )
            for i in range(20)
        ]
        
        created = PostModel.objects.bulk_create(posts)
        self.assertEqual(len(created), 20)
        self.assertEqual(PostModel.objects.filter(path__startswith="/bulk/").count(), 20)
    
    def test_bulk_create_with_custom_models(self):
        """测试批量创建 CustomModel"""
        customs = [
            CustomModel(name=f"custom_{i}", content=f"content_{i}")
            for i in range(15)
        ]
        
        CustomModel.objects.bulk_create(customs)
        self.assertEqual(CustomModel.objects.count(), 15)
    
    def test_bulk_update_posts_status(self):
        """测试批量更新 Posts 状态"""
        for i in range(10):
            PostModel.objects.create(
                title=f"Post {i}",
                filename=f"post_{i}.md",
                path=f"/post/{i}",
                date=1622505600.0,
                status=False
            )
        
        # 批量更新所有 Post 状态为 True
        PostModel.objects.filter(path__startswith="/post/").update(status=True)
        
        updated_posts = PostModel.objects.filter(path__startswith="/post/")
        for post in updated_posts:
            self.assertTrue(post.status)


# ===== 业务逻辑测试 =====
class BusinessLogicTests(TestCase):
    """业务逻辑测试"""
    
    def test_friend_management_workflow(self):
        """测试朋友链接管理工作流"""
        # 创建朋友链接
        friends = []
        for i in range(5):
            friend = FriendModel.objects.create(
                name=f"Friend {i}",
                url=f"https://friend{i}.com",
                imageUrl=f"https://friend{i}.com/avatar.jpg",
                time="2025-01-01",
                description=f"Friend {i} description",
                status=True
            )
            friends.append(friend)
        
        # 验证所有朋友都被创建
        self.assertEqual(FriendModel.objects.count(), 5)
        
        # 验证所有朋友都是活跃的
        active = FriendModel.objects.filter(status=True)
        self.assertEqual(active.count(), 5)
        
        # 禁用一个朋友
        friends[0].status = False
        friends[0].save()
        
        # 验证禁用后的数量
        active = FriendModel.objects.filter(status=True)
        self.assertEqual(active.count(), 4)
    
    def test_post_publication_workflow(self):
        """测试文章发布工作流"""
        # 创建草稿
        draft = PostModel.objects.create(
            title="Draft Post",
            filename="draft.md",
            path="/drafts/draft",
            date=1622505600.0,
            status=False
        )
        
        self.assertFalse(draft.status)
        
        # 发布草稿
        draft.status = True
        draft.save()
        
        # 验证发布状态
        published = PostModel.objects.get(id=draft.id)
        self.assertTrue(published.status)
    
    def test_image_management_workflow(self):
        """测试图片管理工作流"""
        # 上传多个图片
        images = []
        for i in range(5):
            image = ImageModel.objects.create(
                name=f"image_{i}.jpg",
                url=f"https://cdn.example.com/image_{i}.jpg",
                size=f"{100 + i}KB",
                date="2025-01-01",
                type="jpg"
            )
            images.append(image)
        
        self.assertEqual(ImageModel.objects.count(), 5)
        
        # 查询所有 JPG 图片
        jpg_count = ImageModel.objects.filter(type="jpg").count()
        self.assertEqual(jpg_count, 5)


# ===== 统计和计数测试 =====
class StatisticsTests(TestCase):
    """统计和计数功能测试"""
    
    def test_uv_statistic_counting(self):
        """测试 UV 统计计数"""
        # 创建多个 UV 记录
        ips = ["192.168.1.1", "192.168.1.2", "10.0.0.1", "10.0.0.2"]
        for ip in ips:
            StatisticUV.objects.create(ip=ip)
        
        total = StatisticUV.objects.count()
        self.assertEqual(total, 4)
    
    def test_pv_statistic_aggregation(self):
        """测试 PV 统计聚合"""
        # 创建 PV 记录
        StatisticPV.objects.create(url="/page1", number=100)
        StatisticPV.objects.create(url="/page2", number=200)
        StatisticPV.objects.create(url="/page1", number=50)
        
        # 查询特定页面的 PV
        page1_pv = StatisticPV.objects.filter(url="/page1")
        self.assertEqual(page1_pv.count(), 2)
    
    def test_statistic_summary(self):
        """测试统计摘要"""
        # 创建一组统计数据
        for i in range(10):
            StatisticUV.objects.create(ip=f"192.168.1.{i}")
            StatisticPV.objects.create(url=f"/page{i}", number=10 * (i + 1))
        
        uv_total = StatisticUV.objects.count()
        pv_total = StatisticPV.objects.count()
        
        self.assertEqual(uv_total, 10)
        self.assertEqual(pv_total, 10)


# ===== 数据完整性测试 =====
class DataIntegrityTests(TestCase):
    """数据完整性测试"""
    
    def test_post_data_integrity(self):
        """测试 Post 数据完整性"""
        post = PostModel.objects.create(
            title="Integrity Test",
            filename="integrity.md",
            path="/integrity",
            date=1622505600.0,
            status=True
        )
        
        retrieved = PostModel.objects.get(id=post.id)
        
        # 验证所有字段都被正确保存
        self.assertEqual(retrieved.title, "Integrity Test")
        self.assertEqual(retrieved.filename, "integrity.md")
        self.assertEqual(retrieved.path, "/integrity")
        self.assertEqual(retrieved.date, 1622505600.0)
        self.assertTrue(retrieved.status)
    
    def test_image_data_integrity(self):
        """测试 Image 数据完整性"""
        image = ImageModel.objects.create(
            name="integrity.jpg",
            url="https://cdn.example.com/integrity.jpg",
            size="512KB",
            date="2025-01-01",
            type="jpg",
            deleteConfig='{"provider": "aliyun"}'
        )
        
        retrieved = ImageModel.objects.get(id=image.id)
        
        self.assertEqual(retrieved.name, "integrity.jpg")
        self.assertEqual(retrieved.url, "https://cdn.example.com/integrity.jpg")
        self.assertEqual(retrieved.size, "512KB")
        self.assertEqual(retrieved.deleteConfig, '{"provider": "aliyun"}')
    
    def test_friend_data_consistency(self):
        """测试 Friend 数据一致性"""
        friend = FriendModel.objects.create(
            name="Consistency Test",
            url="https://consistency.test",
            imageUrl="https://cdn.example.com/avatar.jpg",
            time="2025-01-01",
            description="A consistency test friend",
            status=True
        )
        
        retrieved = FriendModel.objects.get(id=friend.id)
        
        self.assertEqual(retrieved.name, "Consistency Test")
        self.assertEqual(retrieved.url, "https://consistency.test")
        self.assertEqual(retrieved.status, True)


# ===== 搜索和过滤高级测试 =====
class AdvancedSearchTests(TestCase):
    """搜索和过滤高级测试"""
    
    def setUp(self):
        # 创建测试数据
        for i in range(10):
            PostModel.objects.create(
                title=f"Post {i}",
                filename=f"post_{i}.md",
                path=f"/posts/post_{i}",
                date=1622505600.0 + i * 3600,
                status=(i % 2 == 0)
            )
    
    def test_post_search_by_partial_title(self):
        """测试按标题模糊搜索"""
        results = PostModel.objects.filter(title__contains="Post")
        self.assertEqual(results.count(), 10)
    
    def test_post_filter_by_date_range(self):
        """测试按日期范围过滤"""
        results = PostModel.objects.filter(
            date__gte=1622505600.0,
            date__lte=1622505600.0 + 100000
        )
        self.assertEqual(results.count(), 10)
    
    def test_post_filter_and_order(self):
        """测试过滤后排序"""
        published = PostModel.objects.filter(status=True).order_by("-date")
        
        for i in range(len(published) - 1):
            self.assertGreaterEqual(published[i].date, published[i + 1].date)
    
    def test_post_count_by_status(self):
        """测试按状态计数"""
        published_count = PostModel.objects.filter(status=True).count()
        draft_count = PostModel.objects.filter(status=False).count()
        
        total = published_count + draft_count
        self.assertEqual(total, PostModel.objects.count())


# ===== 缓存操作测试 =====
class CacheOperationTests(TestCase):
    """缓存操作测试"""
    
    def test_cache_create_and_update(self):
        """测试创建和更新缓存"""
        cache = Cache.objects.create(name="cache_test", content="initial")
        
        # 更新缓存内容
        cache.content = "updated"
        cache.save()
        
        retrieved = Cache.objects.get(id=cache.id)
        self.assertEqual(retrieved.content, "updated")
    
    def test_cache_overflow_handling(self):
        """测试缓存溢出处理"""
        # 创建大量缓存
        for i in range(100):
            Cache.objects.create(name=f"cache_{i}", content=f"content_{i}")
        
        total = Cache.objects.count()
        self.assertEqual(total, 100)
    
    def test_cache_expiry_simulation(self):
        """测试缓存过期模拟"""
        cache = Cache.objects.create(name="expiring_cache", content="will_expire")
        
        # 删除缓存模拟过期
        cache.delete()
        
        result = Cache.objects.get_by_name_or_none("expiring_cache")
        self.assertIsNone(result)


# ===== 通知和消息系统测试 =====
class NotificationSystemTests(TestCase):
    """通知和消息系统测试"""
    
    def test_create_multiple_notifications(self):
        """测试创建多个通知"""
        for i in range(5):
            NotificationModel.objects.create(
                label=f"Notification {i}",
                content=f"Content {i}",
                time="2025-01-01"
            )
        
        total = NotificationModel.objects.count()
        self.assertEqual(total, 5)
    
    def test_notification_retrieval(self):
        """测试通知检索"""
        NotificationModel.objects.create(
            label="Test Notif",
            content="Test Content",
            time="2025-01-01"
        )
        
        notif = NotificationModel.objects.filter(label="Test Notif").first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.content, "Test Content")
    
    def test_notification_cleanup(self):
        """测试通知清理"""
        for i in range(10):
            NotificationModel.objects.create(
                label=f"Notif {i}",
                content=f"Content {i}",
                time="2025-01-01"
            )
        
        # 删除所有通知
        NotificationModel.objects.all().delete()
        
        total = NotificationModel.objects.count()
        self.assertEqual(total, 0)


# ===== 设置和配置测试 =====
class SettingsConfigurationTests(TestCase):
    """设置和配置测试"""
    
    def test_setting_get_with_fallback(self):
        """测试获取设置并使用默认值"""
        result = SettingModel.objects.get_content_by_name(
            "NON_EXISTENT",
            "default_value"
        )
        self.assertEqual(result, "default_value")
    
    def test_setting_update_or_create_pattern(self):
        """测试更新或创建模式"""
        setting, created = SettingModel.objects.update_or_create(
            name="PATTERN_TEST",
            defaults={"content": "initial"}
        )
        
        self.assertTrue(created)
        
        # 再次调用应该更新
        setting, created = SettingModel.objects.update_or_create(
            name="PATTERN_TEST",
            defaults={"content": "updated"}
        )
        
        self.assertFalse(created)
        self.assertEqual(setting.content, "updated")
    
    def test_multiple_settings_retrieval(self):
        """测试多个设置检索"""
        settings_names = ["SETTING_1", "SETTING_2", "SETTING_3"]
        
        for name in settings_names:
            SettingModel.objects.create(name=name, content=f"value_{name}")
        
        retrieved = SettingModel.objects.filter(name__in=settings_names)
        self.assertEqual(retrieved.count(), 3)


# ===== 异常和错误处理测试 =====
class ErrorHandlingTests(TestCase):
    """异常和错误处理测试"""
    
    def test_get_nonexistent_cache_returns_none(self):
        """测试获取不存在的缓存返回 None"""
        result = Cache.objects.get_by_name_or_none("definitely_does_not_exist")
        self.assertIsNone(result)
    
    def test_get_content_missing_key_with_default(self):
        """测试获取缺失的 key 时返回默认值"""
        result = Cache.objects.get_content_by_name("missing", "fallback")
        self.assertEqual(result, "fallback")
    
    def test_delete_nonexistent_doesnt_fail(self):
        """测试删除不存在的对象不会失败"""
        posts = PostModel.objects.filter(path="/nonexistent/path")
        posts.delete()  # 不应该抛出异常
        
        self.assertEqual(PostModel.objects.filter(path="/nonexistent/path").count(), 0)
