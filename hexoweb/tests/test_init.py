from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from hexoweb.functions import clear_setting_cache, get_setting_cached, save_setting
from hexoweb.models import SettingModel


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class InitAccessTests(TestCase):
    def setUp(self):
        clear_setting_cache()
        self.addCleanup(clear_setting_cache)
        self.client = Client(enforce_csrf_checks=True)
        self.User = get_user_model()
        self.user_data = {
            "step": "2",
            "username": "new-admin",
            "password": "SetupPassword123!",
            "repassword": "SetupPassword123!",
            "apikey": "replacement-webhook-key",
        }

    def csrf_token(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        return self.client.cookies["csrftoken"].value

    def complete_setup(self):
        self.User.objects.create_superuser(
            username="admin", password="ExistingPassword123!", email=""
        )
        for name, value in {
            "INIT": "6",
            "LANGUAGE": "zh_CN",
            "PROVIDER": '{"provider": "github", "params": {"token": "original-token"}}',
            "WEBHOOK_APIKEY": "original-webhook-key",
            "VERCEL_TOKEN": "original-vercel-token",
            "PROJECT_ID": "original-project",
        }.items():
            save_setting(name, value)
        return self.csrf_token("/login/")

    def settings_snapshot(self):
        return list(SettingModel.objects.order_by("pk").values_list("name", "content"))

    def assert_setup_blocked(self, path, response):
        if path == "/init/":
            self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        else:
            self.assertEqual(response.status_code, 403)
            self.assertFalse(response.json()["status"])

    def test_completed_setup_cannot_create_another_superuser(self):
        token = self.complete_setup()
        original_settings = self.settings_snapshot()

        response = self.client.post("/init/", self.user_data, HTTP_X_CSRFTOKEN=token)

        self.assertFalse(self.User.objects.filter(username="new-admin").exists())
        self.assertEqual(self.User.objects.filter(is_superuser=True).count(), 1)
        self.assertEqual(self.settings_snapshot(), original_settings)
        self.assert_setup_blocked("/init/", response)

    def test_all_setup_steps_are_blocked_after_completion(self):
        token = self.complete_setup()
        payloads = [
            {"step": "1", "language": "en_US"},
            self.user_data,
            {"step": "3", "provider": "github", "token": "replacement-token", "_force": "true"},
            {"step": "4", "id": "replacement-project", "token": "replacement-token"},
        ]
        # Keep the regression test local even when run against vulnerable code.
        with patch("hexoweb.init.update_provider"), patch("hexoweb.init.checkBuilding"), \
                patch("hexoweb.init.request_secret_key_deployment"):
            for completed_step in ("6", "7"):
                for path in ("/init/", "/api/init_step/"):
                    for data in payloads:
                        with self.subTest(completed_step=completed_step, path=path, step=data["step"]):
                            save_setting("INIT", completed_step)
                            original_settings = self.settings_snapshot()
                            original_users = list(self.User.objects.order_by("pk").values())

                            response = self.client.post(path, data, HTTP_X_CSRFTOKEN=token)

                            self.assert_setup_blocked(path, response)
                            self.assertEqual(self.settings_snapshot(), original_settings)
                            self.assertEqual(list(self.User.objects.order_by("pk").values()), original_users)

    def test_completed_setup_blocks_get_and_head(self):
        self.complete_setup()
        original_settings = self.settings_snapshot()
        for path in ("/init/", "/api/init_step/"):
            for method in ("get", "head"):
                with self.subTest(path=path, method=method):
                    response = getattr(self.client, method)(path)
                    if path == "/init/":
                        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
                    else:
                        self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.settings_snapshot(), original_settings)

    def test_completed_setup_is_blocked_for_authenticated_admin(self):
        token = self.complete_setup()
        self.client.force_login(self.User.objects.get(username="admin"))
        original_settings = self.settings_snapshot()
        for path in ("/init/", "/api/init_step/"):
            with self.subTest(path=path):
                response = self.client.post(path, self.user_data, HTTP_X_CSRFTOKEN=token)
                self.assert_setup_blocked(path, response)
                self.assertEqual(self.User.objects.count(), 1)
                self.assertEqual(self.settings_snapshot(), original_settings)

    def test_completed_setup_ignores_stale_process_cache(self):
        token = self.complete_setup()
        for path in ("/init/", "/api/init_step/"):
            with self.subTest(path=path):
                save_setting("INIT", "2")
                self.assertEqual(get_setting_cached("INIT"), "2")
                # Another worker finishes setup without clearing this worker's cache.
                SettingModel.objects.filter(name="INIT").update(content="6")
                original_settings = self.settings_snapshot()

                response = self.client.post(path, self.user_data, HTTP_X_CSRFTOKEN=token)

                self.assert_setup_blocked(path, response)
                self.assertEqual(self.User.objects.count(), 1)
                self.assertEqual(self.settings_snapshot(), original_settings)

    def test_first_setup_can_select_language(self):
        token = self.csrf_token("/init/")
        self.assertEqual(get_setting_cached("INIT"), "1")
        for path in ("/init/", "/api/init_step/"):
            with self.subTest(path=path):
                response = self.client.post(
                    path, {"step": "1", "language": "zh_CN"}, HTTP_X_CSRFTOKEN=token
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(get_setting_cached("INIT"), "2")
                self.assertFalse(self.User.objects.exists())

    def test_first_setup_can_create_superuser_through_html(self):
        self.assert_first_user_created("/init/")

    def test_first_setup_can_create_superuser_through_api(self):
        self.assert_first_user_created("/api/init_step/")

    def assert_first_user_created(self, path):
        save_setting("INIT", "2")
        token = self.csrf_token("/init/")

        response = self.client.post(path, self.user_data, HTTP_X_CSRFTOKEN=token)

        self.assertEqual(response.status_code, 200)
        user = self.User.objects.get(username="new-admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(get_setting_cached("INIT"), "3")

    def test_setup_post_still_requires_csrf(self):
        save_setting("INIT", "2")
        for path in ("/init/", "/api/init_step/"):
            with self.subTest(path=path):
                response = self.client.post(path, self.user_data)
                self.assertEqual(response.status_code, 403)
                self.assertFalse(self.User.objects.exists())
                self.assertEqual(get_setting_cached("INIT"), "2")
