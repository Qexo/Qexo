import os
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, RequestFactory
from django.http import HttpResponse
import requests

from core.secret_key import get_secret_key, BootstrapMiddleware
from hexoweb.functions import VercelUpdate
from hexoweb.libs.vercel import ensure_vercel_secret
from hexoweb import secret_key_migration
from hexoweb.init import InitService
from hexoweb.models import SettingModel


class SecretKeyTests(SimpleTestCase):
    def test_explicit_key_wins(self):
        for env in ({}, {"VERCEL": "1"}):
            with patch.dict(os.environ, {**env, "DJANGO_SECRET_KEY": "private-test-key"}, clear=True):
                self.assertEqual(get_secret_key(), "private-test-key")

    def test_local_key_is_generated_once(self):
        with patch.dict(os.environ, {}, clear=True):
            key = get_secret_key()
            self.assertGreaterEqual(len(key), 64)
            self.assertEqual(get_secret_key(), key)
        with patch.dict(os.environ, {}, clear=True):
            self.assertNotEqual(get_secret_key(), key)

    def test_vercel_has_no_local_signing_key(self):
        with patch.dict(os.environ, {"VERCEL": "1"}, clear=True):
            self.assertEqual(get_secret_key(), "")
            self.assertNotIn("DJANGO_SECRET_KEY", os.environ)

    def test_gunicorn_master_exports_key(self):
        with patch.dict(os.environ, {}, clear=True):
            runpy.run_path("gunicorn.conf.py")
            self.assertEqual(get_secret_key(), os.environ["DJANGO_SECRET_KEY"])


class VercelSecretTests(SimpleTestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"VERCEL": "1"}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.present = {"envs": [{"key": "DJANGO_SECRET_KEY", "target": ["production"]}]}

    @patch("hexoweb.libs.vercel.vercel_request")
    def test_existing_key_is_not_overwritten(self, api):
        api.return_value = self.present
        ensure_vercel_secret("project", "token")
        self.assertEqual(api.call_count, 1)

    @patch("hexoweb.libs.vercel.vercel_request")
    def test_create_only_and_confirm(self, api):
        api.side_effect = [{"envs": []}, {"created": {}}, self.present]
        ensure_vercel_secret("project", "token")
        create = api.call_args_list[1]
        self.assertEqual(create.args[0], "POST")
        self.assertNotIn("upsert", str(create))
        self.assertGreaterEqual(len(create.kwargs["json"]["value"]), 64)

    @patch("hexoweb.libs.vercel.vercel_request")
    def test_concurrent_winner_is_reused(self, api):
        api.side_effect = [{"envs": []}, requests.HTTPError(), self.present, self.present]
        ensure_vercel_secret("project", "token")
        self.assertEqual(sum(c.args[0] == "POST" for c in api.call_args_list), 1)

    @patch("hexoweb.libs.vercel.vercel_request")
    def test_failure_without_existing_key_is_raised(self, api):
        api.side_effect = [{"envs": []}, requests.HTTPError(), {"envs": []}]
        with self.assertRaises(requests.HTTPError):
            ensure_vercel_secret("project", "token")

    @patch("hexoweb.libs.vercel.vercel_request")
    def test_branch_override_is_not_global_key(self, api):
        api.side_effect = [{"envs": [{"key": "DJANGO_SECRET_KEY", "target": ["production"],
                                     "gitBranch": "feature"}]}, {}, self.present]
        ensure_vercel_secret("project", "token")
        self.assertEqual(api.call_args_list[1].args[0], "POST")

    @patch("hexoweb.functions.os.listdir")
    @patch("hexoweb.libs.vercel.getEachFiles", return_value=[])
    @patch("hexoweb.functions.checkBuilding", return_value=0)
    @patch("hexoweb.libs.vercel.vercel_request", return_value={"id": "deployment"})
    def test_bootstrap_reuses_file_deployment_without_tmp_cleanup(self, api, building, files, listing):
        self.assertTrue(VercelUpdate("project", "token", bootstrap=True)["status"])
        self.assertEqual(api.call_args.kwargs["json"]["target"], "production")
        listing.assert_not_called()


class BootstrapTests(TestCase):
    def setUp(self):
        secret_key_migration._attempts.clear()

    def test_only_initialization_routes_are_accessible(self):
        middleware = BootstrapMiddleware(lambda request: HttpResponse("init"))
        factory = RequestFactory()
        self.assertEqual(middleware(factory.get("/init/")).status_code, 200)
        self.assertEqual(middleware(factory.post("/api/auth/")).status_code, 503)
        SettingModel.objects.create(name="INIT", content="6")
        self.assertEqual(middleware(factory.get("/init/")).status_code, 503)

    @patch.dict(os.environ, {"VERCEL": "1", "DJANGO_SECRET_KEY": ""}, clear=True)
    @patch("hexoweb.init.checkBuilding", return_value=0)
    @patch("hexoweb.init.request_secret_key_deployment", side_effect=[False, True])
    def test_deployment_failure_can_be_retried(self, deploy, building):
        service = InitService()
        self.assertFalse(service.handle_vercel_step("project", "token").success)
        self.assertFalse(SettingModel.objects.filter(name="INIT", content="6").exists())
        outcome = service.handle_vercel_step("project", "token")
        self.assertTrue(outcome.success)
        self.assertTrue(outcome.context["redeploy_pending"])

    @patch.dict(os.environ, {"VERCEL": "1", "DJANGO_SECRET_KEY": "provided-key"}, clear=True)
    @patch("hexoweb.init.checkBuilding", return_value=0)
    @patch("hexoweb.init.request_secret_key_deployment")
    def test_provided_key_skips_environment_write_and_redeploy(self, deploy, building):
        outcome = InitService().handle_vercel_step("project", "token")
        self.assertTrue(outcome.success)
        self.assertFalse(outcome.context["redeploy_pending"])
        deploy.assert_not_called()


class ExistingVercelMigrationTests(TestCase):
    def setUp(self):
        secret_key_migration._attempts.clear()
        self.env = patch.dict(os.environ, {"VERCEL": "1"}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        for name, content in {"INIT": "6", "PROJECT_ID": "project", "VERCEL_TOKEN": "token"}.items():
            SettingModel.objects.create(name=name, content=content)
        self.clock = patch("hexoweb.secret_key_migration.monotonic", return_value=100)
        self.now = self.clock.start()
        self.addCleanup(self.clock.stop)
        self.building = patch("hexoweb.secret_key_migration.checkBuilding", return_value=0)
        self.check_building = self.building.start()
        self.addCleanup(self.building.stop)
        self.ensure = patch("hexoweb.secret_key_migration.ensure_vercel_secret")
        self.ensure_secret = self.ensure.start()
        self.addCleanup(self.ensure.stop)
        self.deploy = patch("hexoweb.secret_key_migration.create_file_deployment", return_value={
            "id": "deployment", "readyState": "QUEUED",
        })
        self.create_deployment = self.deploy.start()
        self.addCleanup(self.deploy.stop)

    def test_requests_migrate_independently_of_version_marker(self):
        middleware = BootstrapMiddleware(lambda request: self.fail("Business routes must stay blocked"))
        for marker in ("false", "4.2.0", "4.2.1", ""):
            with self.subTest(marker=marker):
                secret_key_migration._attempts.clear()
                self.create_deployment.reset_mock()
                SettingModel.objects.update_or_create(name="UPDATE_FROM", defaults={"content": marker})
                response = middleware(RequestFactory().get("/login/"))
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response["Retry-After"], "60")
                self.ensure_secret.assert_called_with("project", "token")
                self.create_deployment.assert_called_once_with("project", "token", target="production")
                self.assertEqual(SettingModel.objects.get(name="UPDATE_FROM").content, marker)

    def test_building_defers_and_later_request_retries(self):
        self.check_building.return_value = 1
        self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.ensure_secret.assert_not_called()
        self.create_deployment.assert_not_called()
        self.now.return_value = 159
        self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.assertEqual(self.check_building.call_count, 1)
        self.now.return_value = 160
        self.check_building.return_value = 0
        self.assertTrue(secret_key_migration.try_migrate_secret_key())
        self.create_deployment.assert_called_once()

    def test_api_failure_does_not_prevent_retry_or_log_credentials(self):
        self.ensure_secret.side_effect = requests.HTTPError("private-token-response")
        with self.assertLogs(level="ERROR") as captured:
            self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.assertNotIn("private-token-response", " ".join(captured.output))
        self.create_deployment.assert_not_called()
        self.ensure_secret.side_effect = None
        self.now.return_value = 160
        self.assertTrue(secret_key_migration.try_migrate_secret_key())

    @patch("hexoweb.secret_key_migration.vercel_request", return_value={"readyState": "READY"})
    def test_old_instance_does_not_redeploy_after_ready(self, api):
        self.assertTrue(secret_key_migration.try_migrate_secret_key())
        self.assertTrue(secret_key_migration.try_migrate_secret_key())
        api.assert_not_called()
        self.now.return_value = 160
        self.assertTrue(secret_key_migration.try_migrate_secret_key())
        self.create_deployment.assert_called_once()
        api.assert_called_once_with("GET", "/v13/deployments/deployment", "token")

    @patch("hexoweb.secret_key_migration.vercel_request", return_value={"readyState": "ERROR"})
    def test_failed_deployment_is_retried(self, api):
        self.assertTrue(secret_key_migration.try_migrate_secret_key())
        self.now.return_value = 160
        self.assertTrue(secret_key_migration.try_migrate_secret_key())
        self.assertEqual(self.create_deployment.call_count, 2)

    def test_immediately_failed_deployment_is_not_cached_as_pending(self):
        self.create_deployment.return_value = {"id": "deployment", "readyState": "ERROR"}
        self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.create_deployment.assert_called_once()

    def test_skip_local_explicit_secret_and_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(secret_key_migration.try_migrate_secret_key())
        with patch.dict(os.environ, {"DJANGO_SECRET_KEY": "provided"}):
            self.assertFalse(secret_key_migration.try_migrate_secret_key())
        SettingModel.objects.filter(name="VERCEL_TOKEN").delete()
        self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.check_building.assert_not_called()

    def test_in_progress_attempt_does_not_block_other_requests(self):
        with secret_key_migration._lock:
            self.assertFalse(secret_key_migration.try_migrate_secret_key())
        self.create_deployment.assert_not_called()

    @patch("hexoweb.init.checkBuilding", return_value=0)
    def test_initial_setup_reuses_deployment_started_by_middleware(self, building):
        SettingModel.objects.filter(name="INIT").update(content="4")
        middleware = BootstrapMiddleware(lambda request: HttpResponse("init"))
        self.assertEqual(middleware(RequestFactory().get("/init/")).status_code, 200)
        outcome = InitService().handle_vercel_step("project", "token")
        self.assertTrue(outcome.success)
        self.assertTrue(outcome.context["redeploy_pending"])
        self.create_deployment.assert_called_once()

    @patch("requests.request")
    def test_updater_import_does_not_call_vercel(self, api):
        runpy.run_path("hexoweb/libs/elevator/updater/4_2_1.py")
        api.assert_not_called()


class BootstrapStartupTests(SimpleTestCase):
    def test_build_checks_and_wsgi_startup_with_old_or_missing_version_marker(self):
        # Separate processes ensure URL modules were not imported by the test
        # runner, and use a temporary database instead of the developer's data.
        project_root = Path(__file__).resolve().parents[2]
        prepare = textwrap.dedent("""
            import os
            from unittest.mock import patch
            import django
            django.setup()
            from django.core.management import call_command
            from hexoweb.models import SettingModel
            call_command('migrate', verbosity=0, skip_checks=True)
            for name, content in {
                'INIT': '6', 'PROJECT_ID': 'project', 'VERCEL_TOKEN': 'token',
                'UPDATE_FROM': os.environ['REVIEW_VERSION'],
            }.items():
                SettingModel.objects.create(name=name, content=content)
            with patch('requests.request', side_effect=AssertionError('Build called Vercel')) as api:
                call_command('makemigrations', 'hexoweb', check=True, dry_run=True,
                             interactive=False, verbosity=0, skip_checks=False)
                call_command('migrate', verbosity=0, skip_checks=False)
                assert api.call_count == 0
        """)
        runtime = textwrap.dedent("""
            import sys
            from unittest.mock import Mock, patch
            from django.core.wsgi import get_wsgi_application
            from django.test import RequestFactory
            def api_response(method, url, **kwargs):
                if method == 'GET' and url.endswith('/deployments'):
                    result = {'deployments': []}
                elif method == 'GET' and url.endswith('/env'):
                    result = {'envs': [{'key': 'DJANGO_SECRET_KEY', 'target': ['production']}]}
                elif method == 'POST' and url.endswith('/deployments'):
                    result = {'id': 'deployment', 'readyState': 'QUEUED'}
                else:
                    raise AssertionError('Unexpected request')
                return Mock(json=Mock(return_value=result), raise_for_status=Mock())
            with patch('requests.request', side_effect=api_response) as api:
                with patch('hexoweb.libs.vercel.getEachFiles', return_value=[]):
                    application = get_wsgi_application()
                    for _ in range(2):
                        statuses = []
                        environ = RequestFactory().get('/login/', HTTP_HOST='example.com').environ
                        list(application(environ, lambda status, headers: statuses.append(status)))
                        assert statuses == ['503 Service Unavailable'], statuses
                    posts = [c for c in api.call_args_list if c.args[0] == 'POST']
                    assert len(posts) == 1, api.call_args_list
                    assert posts[0].kwargs['json']['project'] == 'project'
                    assert 'hexoweb.functions' not in sys.modules
        """)
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'bootstrap_test_settings.py'
            settings_file.write_text(
                'from core.settings import *\n'
                'ALLOWED_HOSTS = ["example.com"]\n'
                'DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", '
                f'"NAME": {str(Path(temp_dir) / "bootstrap.sqlite3")!r}' + '}}\n'
            )
            for marker in ('false', '4.2.0', '4.2.1'):
                with self.subTest(marker=marker):
                    database = Path(temp_dir) / 'bootstrap.sqlite3'
                    if database.exists():
                        database.unlink()
                    env = {
                        **os.environ, 'VERCEL': '1', 'VERCEL_ENV': 'production',
                        'DJANGO_SECRET_KEY': '', 'REVIEW_VERSION': marker,
                        'DJANGO_SETTINGS_MODULE': 'bootstrap_test_settings',
                        'PYTHONPATH': os.pathsep.join([temp_dir, str(project_root)]),
                    }
                    for script in (prepare, runtime):
                        result = subprocess.run(
                            [sys.executable, '-c', script], env=env, cwd=project_root,
                            capture_output=True, text=True, timeout=30,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class SecretKeyTranslationTests(SimpleTestCase):
    def test_all_languages_translate_deployment_notice(self):
        from hexoweb.libs.i18n import all_languages, get_language
        for language in all_languages():
            data = get_language(language["name"]).default["data"]
            self.assertTrue(data["INIT_SECRET_REDEPLOY_PENDING"])
