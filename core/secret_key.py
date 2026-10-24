"""Process-local keys for local startup; no per-instance Vercel signing key."""
import os
import secrets


_bootstrap_candidate = None


def get_bootstrap_candidate():
    global _bootstrap_candidate
    if _bootstrap_candidate is None:
        _bootstrap_candidate = secrets.token_urlsafe(64)
    return _bootstrap_candidate


def get_secret_key():
    key = os.environ.get("DJANGO_SECRET_KEY")
    if key:
        return key
    if os.environ.get("VERCEL"):
        get_bootstrap_candidate()  # Generated at startup, never used for signing.
        # Initialization uses cookie CSRF, which does not require SECRET_KEY.
        # An empty key also makes accidental Django signing fail closed.
        return ""
    key = secrets.token_urlsafe(64)
    os.environ["DJANGO_SECRET_KEY"] = key
    return key


class BootstrapMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.contrib.auth.models import AnonymousUser
        from django.http import HttpResponse
        from hexoweb.models import SettingModel
        from hexoweb.secret_key_migration import try_migrate_secret_key

        try_migrate_secret_key()
        init_value = SettingModel.objects.filter(name="INIT").values_list("content", flat=True).first()
        if (request.path not in {"/init/", "/api/init_step/"}
                or int(init_value or 1) >= 6):
            response = HttpResponse(
                "DJANGO_SECRET_KEY 尚未生效。首次部署请访问 /init/ 完成 Vercel 配置；"
                "已提交配置请等待新部署完成。已有项目会自动迁移密钥，失败后将重试；"
                "也可在 Vercel 设置密钥并重新部署。",
                status=503,
            )
            response["Retry-After"] = "60"
            return response
        request.user = AnonymousUser()
        request.session = {}
        return self.get_response(request)
