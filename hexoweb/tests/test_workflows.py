from django.test import TestCase, Client
from django.contrib.auth.models import User

from hexoweb.models import (
    Cache,
    SettingModel,
    ImageModel,
    FriendModel,
    NotificationModel,
    PostModel,
    StatisticUV,
    StatisticPV,
)


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
