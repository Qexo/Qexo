from django.test import SimpleTestCase, TestCase, Client
from django.urls import resolve, reverse
from django.contrib.auth.models import User


class UrlSmokeTests(SimpleTestCase):
    def test_home_url(self):
        self.assertEqual(reverse("home"), "/")

    def test_login_url(self):
        self.assertEqual(reverse("login"), "/login/")

    def test_api_auth_url_resolves(self):
        self.assertEqual(resolve("/api/auth/").view_name, "auth")


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
