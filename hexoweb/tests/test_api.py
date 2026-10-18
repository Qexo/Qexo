import json

from django.test import TestCase, Client
from django.contrib.auth.models import User


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
