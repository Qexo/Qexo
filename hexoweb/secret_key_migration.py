"""Runtime secret-key bootstrap, independent of UPDATE_FROM and build checks."""
import logging
import os
from threading import Lock
from time import monotonic
from urllib.parse import quote

import requests

from hexoweb.libs.vercel import (
    checkBuilding, create_file_deployment, ensure_vercel_secret, vercel_request,
)
from hexoweb.models import SettingModel


RETRY_SECONDS = 60
_lock = Lock()
_attempts = {}  # Process-local cooldown and deployment receipt; no schema changes.


def request_secret_key_deployment(project, token):
    """Start or monitor a bootstrap deployment; API failures remain retryable."""
    if not _lock.acquire(blocking=False):
        return False
    target = os.environ.get("VERCEL_ENV", "production")
    state = _attempts.setdefault(
        (project, target), {"retry_after": 0, "deployment_id": "", "pending": False},
    )
    attempted = False
    try:
        if monotonic() < state["retry_after"]:
            return state["pending"]
        attempted = True
        if state["deployment_id"]:
            try:
                deployment = vercel_request(
                    "GET", "/v13/deployments/" + quote(state["deployment_id"], safe=""), token,
                )
            except requests.HTTPError as error:
                if error.response is None or error.response.status_code != 404:
                    raise
                deployment = {"readyState": "CANCELED"}
            if deployment.get("readyState") not in {"ERROR", "CANCELED"}:
                # Old URLs stay blocked even after READY. Only a new instance
                # with the injected private key can serve normal requests.
                return True
            state["deployment_id"] = ""
            state["pending"] = False
        if checkBuilding(project, token):
            return False
        ensure_vercel_secret(project, token)
        deployment = create_file_deployment(project, token, target=target)
        state["deployment_id"] = deployment["id"]
        state["pending"] = deployment.get("readyState") not in {"ERROR", "CANCELED"}
        return state["pending"]
    except Exception:
        # Do not log exception text/API bodies, which can contain credentials.
        logging.error("Qexo SECRET_KEY migration deferred; retrying on a later request")
        return False
    finally:
        if attempted:
            state["retry_after"] = monotonic() + RETRY_SECONDS
        _lock.release()


def try_migrate_secret_key():
    """Run before bootstrap rejects requests, using existing saved credentials."""
    if not os.environ.get("VERCEL") or os.environ.get("DJANGO_SECRET_KEY"):
        return False
    try:
        values = dict(SettingModel.objects.filter(
            name__in=["PROJECT_ID", "VERCEL_TOKEN"],
        ).values_list("name", "content"))
        project, token = values.get("PROJECT_ID"), values.get("VERCEL_TOKEN")
        if not project or not token:
            return False  # First-time installations still need the setup form.
        return request_secret_key_deployment(project, token)
    except Exception:
        logging.error("Qexo SECRET_KEY migration unavailable; retrying on a later request")
        return False
