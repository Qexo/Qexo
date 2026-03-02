from unittest import TestCase

from core.session_engine import get_session_engine


class SessionEngineTests(TestCase):
    def test_uses_signed_cookies_on_vercel(self):
        self.assertEqual(
            get_session_engine(True),
            "django.contrib.sessions.backends.signed_cookies",
        )

    def test_uses_db_backend_off_vercel(self):
        self.assertEqual(
            get_session_engine(False),
            "django.contrib.sessions.backends.db",
        )
