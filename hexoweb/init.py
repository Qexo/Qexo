import json
import random
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model

import hexoweb.libs.i18n
from core.qexoSettings import ALL_SETTINGS
from hexoweb.functions import (
    checkBuilding,
    check_if_vercel,
    gettext,
    get_setting_cached,
    save_setting,
    update_language,
    update_provider,
    verify_provider,
)
from hexoweb.libs.platforms import all_configs as platform_configs
from hexoweb.libs.platforms import all_providers, get_params
from hexoweb.models import SettingModel


@dataclass
class StepOutcome:
    success: bool
    step: str
    msg: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class InitService:
    def __init__(self) -> None:
        self.User = get_user_model()
        # all_languages returns a list of dicts like {"name": "zh_CN", "name_local": "中文(简体)"}
        self.allowed_languages = {lang.get("name") for lang in hexoweb.libs.i18n.all_languages() if lang.get("name")}

    # ---------- shared helpers ----------
    def normalize_step(self, step: Optional[str]) -> str:
        return str(step) if step else "1"

    def seed_missing_settings(self) -> None:
        existing = set(SettingModel.objects.values_list("name", flat=True))
        for name, default, _reset, _desc in ALL_SETTINGS:
            if name not in existing:
                save_setting(name, default)

    def ensure_webhook_apikey(self, apikey: Optional[str]) -> None:
        if apikey:
            save_setting("WEBHOOK_APIKEY", apikey)
            return
        if not SettingModel.objects.filter(name="WEBHOOK_APIKEY").exists():
            save_setting(
                "WEBHOOK_APIKEY",
                "".join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for _ in range(12)),
            )

    def build_provider_context(self, provider_value: Optional[Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {"all_providers": {}, "all_platform_configs": platform_configs()}
        for provider in all_providers():
            context["all_providers"][provider] = get_params(provider)
        if provider_value:
            if isinstance(provider_value, str):
                try:
                    provider_value = json.loads(provider_value)
                except (ValueError, TypeError):
                    pass
                    # 如果 provider_value 不是有效的 JSON，保留原始字符串
            context["PROVIDER"] = json.dumps(provider_value)
        return context

    def _boolish(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).lower() in {"1", "true", "on", "yes", "y"}

    # ---------- step handlers ----------
    def handle_language_step(self, language: Optional[str], has_users: bool) -> StepOutcome:
        if not language or language not in self.allowed_languages:
            return StepOutcome(False, "1", gettext("INIT_LANGUAGE_INVALID"))

        self.seed_missing_settings()
        save_setting("INIT", "2")
        save_setting("LANGUAGE", language)
        update_language()

        next_step = "2" if not has_users else "3"
        context: Dict[str, Any] = {}
        if next_step == "3":
            context.update(self.build_provider_context(get_setting_cached("PROVIDER")))
        return StepOutcome(True, next_step, None, context)

    def handle_user_step(
        self,
        username: Optional[str],
        password: Optional[str],
        repassword: Optional[str],
        apikey: Optional[str],
    ) -> StepOutcome:
        if repassword != password:
            return StepOutcome(False, "2", gettext("RESET_PASSWORD_NO_MATCH"), {
                "username": username,
                "password": password,
                "repassword": repassword,
                "apikey": apikey,
            })
        if not password:
            return StepOutcome(False, "2", gettext("RESET_PASSWORD_NO"), {
                "username": username,
                "password": password,
                "repassword": repassword,
                "apikey": apikey,
            })
        if not username:
            return StepOutcome(False, "2", gettext("RESET_PASSWORD_NO_USERNAME"), {
                "username": username,
                "password": password,
                "repassword": repassword,
                "apikey": apikey,
            })
        if self.User.objects.filter(username=username).exists():
            return StepOutcome(False, "2", gettext("USERNAME_EXISTS"), {
                "username": username,
                "password": password,
                "repassword": repassword,
                "apikey": apikey,
            })

        self.ensure_webhook_apikey(apikey)
        self.User.objects.create_superuser(username=username, password=password, email="")
        save_setting("INIT", "3")
        context = self.build_provider_context(get_setting_cached("PROVIDER"))
        return StepOutcome(True, "3", None, context)

    def _normalize_provider_payload(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        provider_raw = post_data.get("provider")
        provider_name = provider_raw[0] if isinstance(provider_raw, (list, tuple)) else provider_raw
        params: Dict[str, Any] = {}
        for key, value in post_data.items():
            if key in {"provider", "step", "csrfmiddlewaretoken"}:
                continue
            # request.POST may provide lists; keep first element for compatibility
            if isinstance(value, (list, tuple)):
                params[key] = value[0]
            else:
                params[key] = value
        return {"provider": provider_name, "params": params}

    def _build_verify_error(self, verify: Dict[str, Any]) -> str:
        if verify.get("status") == -1:
            return gettext("VERIFY_FAILED") or "远程连接错误"

        issues = []
        if not verify.get("hexo"):
            issues.append(gettext("HEXO_VERSION_FAILED"))
        if not verify.get("indexhtml"):
            issues.append(gettext("HEXO_INDEX_FAILED"))
        if not verify.get("config_hexo"):
            issues.append(gettext("HEXO_CONFIG_FAILED"))
        if not verify.get("theme_dir"):
            issues.append(gettext("HEXO_THEME_FAILED"))
        if not verify.get("package"):
            issues.append(gettext("HEXO_PACKAGE_FAILED"))
        if not verify.get("source"):
            issues.append(gettext("HEXO_SOURCE_FAILED"))

        if not issues and verify.get("hexo"):
            return gettext("HEXO_VERSION").format(verify.get("hexo"))
        return "<br>".join(issues)

    def handle_provider_step(self, post_data: Dict[str, Any]) -> StepOutcome:
        provider_payload = self._normalize_provider_payload(post_data)
        provider_name = provider_payload.get("provider")
        if not provider_name:
            context = self.build_provider_context(get_setting_cached("PROVIDER"))
            return StepOutcome(False, "3", gettext("PROVIDER_REQUIRED"), context)

        params = provider_payload.get("params", {})
        config_type = params.get("config")
        # 非Hexo配置或明确强制时，自动进行强制提交
        is_force = self._boolish(params.get("_force")) or (config_type != "Hexo")
        provider_payload["params"] = params

        context = self.build_provider_context(provider_payload)
        # 移除内部标记字段
        if "_force" in params:
            params.pop("_force", None)
        try:
            if not is_force:
                verify = verify_provider(provider_payload)
                if verify.get("status") != 1:
                    msg = self._build_verify_error(verify)
                    return StepOutcome(False, "3", msg, context)
            save_setting("PROVIDER", json.dumps(provider_payload))
            update_provider()
        except Exception as e:
            return StepOutcome(False, "3", str(e), context)
        step = "4" if check_if_vercel() else "6"
        save_setting("INIT", step)

        if step == "4":
            context["project_id"] = get_setting_cached("PROJECT_ID") or os.environ.get("VERCEL_PROJECT_ID")
            context["vercel_token"] = get_setting_cached("VERCEL_TOKEN") or None
        else:
            user = self.User.objects.first()
            if user:
                context["username"] = user.username
        return StepOutcome(True, step, None, context)

    def handle_vercel_step(self, project_id: Optional[str], vercel_token: Optional[str]) -> StepOutcome:
        if not project_id or not vercel_token:
            return StepOutcome(False, "4", gettext("VERIFY_FAILED"), {
                "project_id": project_id,
                "vercel_token": vercel_token,
            })
        try:
            checkBuilding(project_id, vercel_token)
            save_setting("VERCEL_TOKEN", vercel_token)
            save_setting("PROJECT_ID", project_id)
            save_setting("INIT", "6")
            # Get username for final step context
            context = {}
            user = self.User.objects.first()
            if user:
                context["username"] = user.username
            return StepOutcome(True, "6", None, context)
        except Exception:
            return StepOutcome(False, "4", gettext("VERIFY_FAILED"), {
                "project_id": project_id,
                "vercel_token": vercel_token,
            })