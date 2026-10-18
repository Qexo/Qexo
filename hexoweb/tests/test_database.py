import uuid

from django.db import IntegrityError
from django.test import TestCase

from hexoweb.models import (
    Cache,
    SettingModel,
    ImageModel,
    FriendModel,
    CustomModel,
    PostModel,
    StatisticUV,
)


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
