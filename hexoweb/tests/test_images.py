import json
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, Client
from django.contrib.auth.models import User

from hexoweb.models import ImageModel
from hexoweb.libs.image.providers.cfimgbed import (
    Main as CFImgBedMain,
    delete as cfimgbed_delete,
)


class CFImgBedProviderTests(SimpleTestCase):
    def test_params_hide_fixed_fields(self):
        self.assertNotIn("post_params", CFImgBedMain.params)
        self.assertNotIn("delete_url", CFImgBedMain.params)

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.post")
    def test_upload_sends_detected_content_type_when_file_content_type_missing(self, mock_post):
        mock_response = Mock()
        mock_response.text = '[{"src":"/file/test.png"}]'
        mock_response.json.return_value = [{"src": "/file/test.png"}]
        mock_post.return_value = mock_response

        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            api_key="",
        )
        upload_file = SimpleUploadedFile("test.png", b"123", content_type=None)

        provider.upload(upload_file)

        files_payload = mock_post.call_args.kwargs["files"]["file"]
        self.assertEqual(files_payload[0], "test.png")
        self.assertEqual(files_payload[1], b"123")
        self.assertEqual(files_payload[2], "image/png")

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.post")
    def test_upload_uses_plain_text_when_response_is_not_json(self, mock_post):
        mock_response = Mock()
        mock_response.text = "https://img.example.com/uploads/test.png"
        mock_response.json.side_effect = json.JSONDecodeError("not json", "", 0)
        mock_post.return_value = mock_response

        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            json_path="0.src",
            api_key="",
            custom_url="",
        )
        upload_file = SimpleUploadedFile("test.png", b"123", content_type="image/png")

        url, delete_config = provider.upload(upload_file)

        self.assertEqual(url, "https://img.example.com/uploads/test.png")
        self.assertEqual(delete_config, {})

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.post")
    def test_upload_keeps_json_path_behavior_for_json_response(self, mock_post):
        mock_response = Mock()
        mock_response.text = '[{"src":"/file/test.png"}]'
        mock_response.json.return_value = [{"src": "/file/test.png"}]
        mock_post.return_value = mock_response

        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            json_path="0.src",
            api_key="",
            custom_url="https://img.example.com",
        )
        upload_file = SimpleUploadedFile("test.png", b"123", content_type="image/png")

        url, delete_config = provider.upload(upload_file)

        self.assertEqual(url, "https://img.example.com/file/test.png")
        self.assertEqual(delete_config["delete_url"], "https://img.example.com/api/manage/delete/test.png")

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.post")
    def test_upload_persists_auth_code_in_delete_config(self, mock_post):
        mock_response = Mock()
        mock_response.text = '[{"src":"/file/test.png"}]'
        mock_response.json.return_value = [{"src": "/file/test.png"}]
        mock_post.return_value = mock_response

        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            auth_code="auth123",
            custom_url="https://img.example.com",
        )
        upload_file = SimpleUploadedFile("test.png", b"123", content_type="image/png")

        _, delete_config = provider.upload(upload_file)

        self.assertEqual(delete_config["auth_code"], "auth123")
        self.assertEqual(delete_config["delete_url"], "https://img.example.com/api/manage/delete/test.png")

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.delete")
    def test_delete_sends_auth_code_as_query_param(self, mock_delete):
        mock_delete.return_value = Mock(text='{"success": true}')
        config = {
            "provider": "CFImgBed",
            "delete_url": "https://img.example.com/api/manage/delete/test.png",
            "auth_code": "auth123",
        }

        result = cfimgbed_delete(config)

        self.assertEqual(result, '{"success": true}')
        mock_delete.assert_called_once_with(
            "https://img.example.com/api/manage/delete/test.png",
            headers={},
            params={"authCode": "auth123"},
        )

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.post")
    def test_upload_builds_query_params_from_official_api(self, mock_post):
        mock_response = Mock()
        mock_response.text = '[{"src":"/file/test.png"}]'
        mock_response.json.return_value = [{"src": "/file/test.png"}]
        mock_post.return_value = mock_response

        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            api_key="",
            auth_code="auth123",
            upload_channel="telegram",
            server_compress="false",
            auto_retry="false",
            return_format="default",
        )
        upload_file = SimpleUploadedFile("test.png", b"123", content_type="image/png")
        provider.upload(upload_file)

        params = mock_post.call_args.kwargs["params"]
        self.assertEqual(params["authCode"], "auth123")
        self.assertEqual(params["uploadChannel"], "telegram")
        self.assertEqual(params["serverCompress"], "false")
        self.assertEqual(params["autoRetry"], "false")
        self.assertEqual(params["returnFormat"], "default")

    @patch("hexoweb.libs.image.providers.cfimgbed.requests.post")
    def test_upload_omits_optional_query_params_when_unset(self, mock_post):
        mock_response = Mock()
        mock_response.text = '[{"src":"/file/test.png"}]'
        mock_response.json.return_value = [{"src": "/file/test.png"}]
        mock_post.return_value = mock_response

        provider = CFImgBedMain(api="https://api.example.com/upload")
        upload_file = SimpleUploadedFile("test.png", b"123", content_type="image/png")
        provider.upload(upload_file)

        params = mock_post.call_args.kwargs["params"]
        self.assertNotIn("serverCompress", params)
        self.assertNotIn("autoRetry", params)
        self.assertNotIn("returnFormat", params)


class CFImgBedDirectUploadTests(SimpleTestCase):
    def test_direct_config_uses_auth_code_without_exposing_api_key(self):
        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            api_key="imgbed_secret",
            auth_code="upload-only",
            upload_channel="cfr2",
        )

        config = provider.direct_upload_config()

        self.assertEqual(config["url"], "https://api.example.com/upload")
        self.assertEqual(config["headers"], {})
        self.assertEqual(config["params"]["authCode"], "upload-only")
        self.assertEqual(config["params"]["uploadChannel"], "cfr2")
        self.assertNotIn("imgbed_secret", json.dumps(config))

    def test_direct_config_uses_api_key_when_auth_code_is_missing(self):
        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            api_key="imgbed_secret",
        )

        config = provider.direct_upload_config()

        self.assertEqual(config["headers"], {"Authorization": "Bearer imgbed_secret"})
        self.assertNotIn("authCode", config["params"])

    def test_complete_direct_upload_rejects_unexpected_host(self):
        provider = CFImgBedMain(
            api="https://api.example.com/upload",
            auth_code="upload-only",
            custom_url="https://img.example.com",
        )

        with self.assertRaisesRegex(ValueError, "unexpected host"):
            provider.complete_direct_upload("https://attacker.example/file/test.png")


class CFImgBedDirectUploadApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="image_user", password="image_pass")
        self.client.force_login(self.user)
        self.image_host = {
            "type": "CFImgBed",
            "params": {
                "api": "https://api.example.com/upload",
                "api_key": "imgbed_secret",
                "auth_code": "upload-only",
                "custom_url": "https://img.example.com",
            },
        }

    @patch("hexoweb.api.get_setting_cached")
    def test_config_endpoint_returns_direct_config_without_api_key(self, mock_setting):
        mock_setting.return_value = json.dumps(self.image_host)

        response = self.client.get("/api/upload/config/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["direct"])
        self.assertEqual(payload["provider"], "CFImgBed")
        self.assertEqual(payload["config"]["params"]["authCode"], "upload-only")
        self.assertNotIn("imgbed_secret", response.content.decode("utf-8"))
        self.assertEqual(response["Cache-Control"], "no-store")

    @patch("hexoweb.api.get_setting_cached")
    def test_config_endpoint_supports_api_key_only_bearer_upload(self, mock_setting):
        api_key_host = json.loads(json.dumps(self.image_host))
        api_key_host["params"]["auth_code"] = ""
        mock_setting.return_value = json.dumps(api_key_host)

        response = self.client.get("/api/upload/config/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["direct"])
        self.assertEqual(
            payload["config"]["headers"],
            {"Authorization": "Bearer imgbed_secret"},
        )
        self.assertNotIn("authCode", payload["config"]["params"])

    @patch("hexoweb.api.get_setting_cached")
    def test_complete_endpoint_records_direct_upload_and_server_delete_credentials(self, mock_setting):
        mock_setting.return_value = json.dumps(self.image_host)

        response = self.client.post("/api/upload/complete/", {
            "remote_url": "/file/test.png",
            "name": "test.png",
            "size": "6291456",
            "content_type": "image/png",
        })

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["status"])
        self.assertEqual(payload["url"], "https://img.example.com/file/test.png")
        image = ImageModel.objects.get(name="test.png")
        self.assertEqual(image.size, "6291456")
        delete_config = json.loads(image.deleteConfig)
        self.assertEqual(delete_config["provider"], "CFImgBed")
        self.assertEqual(delete_config["api_key"], "imgbed_secret")
        self.assertEqual(delete_config["auth_code"], "upload-only")

    @patch("hexoweb.api.get_setting_cached")
    def test_complete_endpoint_rejects_unexpected_remote_host(self, mock_setting):
        mock_setting.return_value = json.dumps(self.image_host)

        response = self.client.post("/api/upload/complete/", {
            "remote_url": "https://attacker.example/file/test.png",
            "name": "test.png",
            "size": "1",
            "content_type": "image/png",
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["status"])
        self.assertEqual(ImageModel.objects.count(), 0)
