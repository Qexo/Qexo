import json

from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase, TestCase, Client
from django.contrib.auth.models import User

from hexoweb.models import PostModel, TalkModel


class SQLiteMigrationSmokeTests(TransactionTestCase):
    databases = {"default"}

    def test_default_sqlite_database_can_run_migrate(self):
        self.assertEqual(connection.vendor, "sqlite")
        call_command("migrate", database="default", interactive=False, verbosity=0)
        self.assertIn("django_migrations", connection.introspection.table_names())


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
