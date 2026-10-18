"""Vercel helpers with no migration or application-startup side effects."""
import logging
import os
from urllib.parse import quote

import requests


def vercel_request(method, path, token, **kwargs):
    """Shared Vercel transport. Never log response bodies containing secrets."""
    params = dict(kwargs.pop("params", {}))
    if os.environ.get("VERCEL_TEAM_ID"):
        params["teamId"] = os.environ["VERCEL_TEAM_ID"]
    response = requests.request(
        method, "https://api.vercel.com" + path,
        headers={"Authorization": "Bearer " + token},
        params=params, timeout=30, **kwargs,
    )
    response.raise_for_status()
    return response.json()


def ensure_vercel_secret(project_id, token):
    """Create only: a concurrent winner's environment variable is never replaced."""
    from core.secret_key import get_bootstrap_candidate

    path = "/v10/projects/" + quote(project_id, safe="") + "/env"
    target = os.environ.get("VERCEL_ENV", "production")
    if target not in {"production", "preview", "development"}:
        raise ValueError("Unsupported Vercel environment")

    def exists():
        result = vercel_request("GET", path, token)
        return any(env.get("key") == "DJANGO_SECRET_KEY"
                   and target in env.get("target", [])
                   and not env.get("gitBranch")
                   for env in result["envs"])

    if exists():
        return
    try:
        result = vercel_request("POST", path, token, json={
            "key": "DJANGO_SECRET_KEY", "value": get_bootstrap_candidate(),
            "type": "encrypted", "target": [target],
        })  # Deliberately no upsert=true.
        if result.get("error") or result.get("failed"):
            raise ValueError("Vercel environment creation failed")
    except (requests.RequestException, ValueError):
        # Includes conflicts and ambiguous timeouts after a successful write.
        if not exists():
            raise
    if not exists():
        raise ValueError("Vercel environment creation was not confirmed")


def checkBuilding(projectId, token):
    result = vercel_request("GET", "/v6/deployments", token,
                            params={"projectId": projectId})["deployments"]
    return sum(d.get("state") in {"QUEUED", "BUILDING", "INITIALIZING"}
               for d in result)


def file_get_contents(file):
    try:
        with open(file, 'r', encoding="utf8") as f:
            content = f.read()
        return content
    except (OSError, UnicodeDecodeError) as e:
        logging.warning("Read deployment file" + ": " + file + " -> " + repr(e))
        return False


def getEachFiles(base, path=""):
    file = list()
    current_dir = os.path.join(base, path)
    try:
        handler = os.listdir(current_dir)
    except OSError as e:
        logging.warning("Read deployment file" + ": " + current_dir + " -> " + repr(e))
        return file
    for item in handler:
        if item != '.git':
            fromfile = os.path.join(current_dir, item)
            rel_path = os.path.join(path, item)
            if os.path.isdir(fromfile):
                file += getEachFiles(base, rel_path)
            else:
                content = file_get_contents(fromfile)
                if content is False:
                    continue
                file.append({"file": rel_path,
                             "data": content})
    return file


def create_file_deployment(project_id, token, source_path="", *, target="production"):
    """Submit deployment files without importing application startup code."""
    data = {
        "name": "qexo", "project": project_id, "target": target,
        "files": getEachFiles(source_path or os.path.abspath("")),
    }
    response = vercel_request("POST", "/v13/deployments", token, json=data)
    if response.get("error") or not response.get("id"):
        raise ValueError("Vercel deployment creation failed")
    return response
