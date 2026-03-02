from django.test import SimpleTestCase
from django.urls import resolve


class PasskeyTrailingSlashURLTests(SimpleTestCase):
    def test_passkey_reg_begin_with_trailing_slash_is_routable(self):
        self.assertEqual(resolve("/passkeys/reg/begin/").func.__name__, "reg_begin")
