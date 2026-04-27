"""
@Project   : cfimgbed
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

import json
import mimetypes
import requests
import logging
from urllib.parse import urlsplit

from ..core import Provider
from ..replace import replace_folder_path


def delete(config):
    headers = {}
    if config.get("api_key"):
        headers['Authorization'] = f"Bearer {config.get('api_key')}"
    auth_code = config.get("auth_code")

    delete_url = config.get("delete_url")
    if not delete_url:
        logging.warning("Delete URL is not configured; remote delete is not supported.")
        return "Delete URL not configured; remote delete not supported."

    response = requests.delete(
        delete_url,
        headers=headers,
        params={"authCode": auth_code} if auth_code else None
    )
    return response.text


class Main(Provider):
    name = 'CFImgBed'

    params = {
        'api': {'description': 'API 地址', 'placeholder': '图床图片上传的 API，例如：https://example.com/upload'},
        'api_key': {'description': 'API 密钥', 'placeholder': '例如：imgbed_XXXXXXXXX'},
        'auth_code': {'description': '上传认证码', 'placeholder': '上传认证码（可选，和 API 密钥二选一）'},
        'custom_url': {'description': '自定义访问域名', 'placeholder': '例如：https://example.com（可选）'},
        'upload_channel': {'description': '上传渠道', 'placeholder': '可选：telegram, cfr2, s3, discord, huggingface（默认 telegram）'},
        'channel_name': {'description': '渠道名称', 'placeholder': '多渠道场景可选'},
        'server_compress': {'description': '服务端压缩', 'placeholder': '可选：true/false（默认 true）'},
        'auto_retry': {'description': '失败自动重试', 'placeholder': '可选：true/false（默认 true）'},
        'return_format': {'description': '返回链接格式', 'placeholder': '可选：default/full（默认 default）'},
        'upload_folder': {'description': '上传的文件夹', 'placeholder': '图床保存的文件夹'},
        'upload_name_type': {'description': '文件命名规则', 'placeholder': '可选：default, index, origin, short (默认: default)'}
    }

    def __init__(
            self,
            api,
            api_key="",
            auth_code="",
            custom_url="",
            upload_channel="",
            channel_name="",
            server_compress=None,
            auto_retry=None,
            return_format="",
            upload_folder="",
            upload_name_type="default",
            json_path="0.src",
            post_params="file",
            delete_url="",
            **kwargs
    ):
        self.api = api
        self.post_params = post_params
        self.json_path = json_path
        self.api_key = api_key
        self.custom_url = custom_url
        self.delete_url = delete_url
        self.auth_code = auth_code
        self.upload_channel = upload_channel
        self.channel_name = channel_name
        self.server_compress = server_compress
        self.auto_retry = auto_retry
        self.return_format = return_format
        self.upload_folder = upload_folder
        self.upload_name_type = upload_name_type

    def upload(self, file):
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        file_name = getattr(file, "name", "") or "upload.bin"
        content_type = getattr(file, "content_type", None) or mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        # 使用 requests 的 params 参数构造并编码查询参数，避免手写字符串拼接
        params = {}
        if self.auth_code:
            params["authCode"] = self.auth_code

        if self.upload_channel:
            params["uploadChannel"] = self.upload_channel

        if self.channel_name:
            params["channelName"] = self.channel_name

        if self._should_include_param(self.server_compress):
            params["serverCompress"] = self._format_bool(self.server_compress, True)

        if self._should_include_param(self.auto_retry):
            params["autoRetry"] = self._format_bool(self.auto_retry, True)

        if self.return_format:
            params["returnFormat"] = self.return_format

        if self.upload_folder:
            folder_path = replace_folder_path(self.upload_folder)
            params["uploadFolder"] = folder_path

        if self.upload_name_type:
            params["uploadNameType"] = self.upload_name_type

        response = requests.post(
            self.api,
            headers=headers,
            params=params or None,
            files={"file": [file_name, file.read(), content_type]},
        )
        data = response.text
        logging.info(data)
        if self.json_path:
            json_path = self.json_path.split(".")
            response.encoding = "utf8"
            try:
                url = response.json()
            except json.JSONDecodeError:
                url = data
            if isinstance(url, (dict, list)):
                for path in json_path:
                    if isinstance(url, list):  # 处理列表Index
                        url = url[int(path)]
                    else:
                        url = url[path]
        else:
            url = data
            
        image_url = self._full_url(str(url))
        delete_full_url = self._build_delete_url(str(url))
        if delete_full_url:
            return [image_url, {
                "provider": Main.name,
                "delete_url": delete_full_url,
                "api_key": self.api_key,
                "auth_code": self.auth_code,
            }]
        return [image_url, {}]

    def _base_url(self):
        if self.custom_url:
            return self.custom_url.rstrip("/")
        parsed = urlsplit(self.api)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return ""

    def _full_url(self, url):
        if url.startswith("http://") or url.startswith("https://"):
            return url
        base_url = self._base_url()
        if not base_url:
            return url
        if url.startswith("/"):
            return f"{base_url}{url}"
        return f"{base_url}/{url}"

    def _build_delete_url(self, url):
        d_path = self._extract_delete_path(url)
        if not d_path:
            return ""
        delete_base = self.delete_url.rstrip("/") if self.delete_url else f"{self._base_url()}/api/manage/delete"
        if not delete_base:
            return ""
        parsed_delete_base = urlsplit(delete_base)
        if not (parsed_delete_base.scheme and parsed_delete_base.netloc):
            return ""
        return f"{delete_base}/{d_path}"

    @staticmethod
    def _extract_delete_path(url):
        path = urlsplit(url).path if url.startswith("http://") or url.startswith("https://") else url
        if path.startswith('/file/'):
            return path[6:].lstrip("/")
        if path == '/file':
            return ""
        return ""

    @staticmethod
    def _format_bool(value, default):
        if isinstance(value, bool):
            return "true" if value else "false"
        value_str = str(value).strip().lower()
        if value_str in {"1", "true", "yes", "on"}:
            return "true"
        if value_str in {"0", "false", "no", "off"}:
            return "false"
        return "true" if default else "false"

    @staticmethod
    def _should_include_param(value):
        return value is not None and value != ""
