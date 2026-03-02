from django.test import SimpleTestCase
from django.urls import resolve


class PasskeyTrailingSlashURLTests(SimpleTestCase):
    def test_passkey_api_with_trailing_slash_is_routable(self):
        routes = {
            "/passkeys/auth/begin/": "auth_begin",
            "/passkeys/auth/complete/": "auth_complete",
            "/passkeys/reg/begin/": "reg_begin",
            "/passkeys/reg/complete/": "reg_complete",
        }
        for route, view_name in routes.items():
            with self.subTest(route=route):
                self.assertEqual(resolve(route).func.__name__, view_name)
