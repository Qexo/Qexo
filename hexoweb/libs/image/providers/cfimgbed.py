"""
@Project   : cfimgbed
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

import json
import requests
import logging

from ..core import Provider
from ..replace import replace_folder_path


def delete(config):
    headers = {}
    if config.get("api_key"):
        headers['Authorization'] = f"Bearer {config.get('api_key')}"

    delete_url = config.get("delete_url")
    if not delete_url:
        logging.warning("Delete URL is not configured; remote delete is not supported.")
        return "Delete URL not configured; remote delete not supported."

    response = requests.delete(delete_url, headers=headers)
    return response.text


class Main(Provider):
    name = 'CFImgBed'

    params = {
        'api': {'description': 'API 地址', 'placeholder': '图床图片上传的 API，例如：https://example.com/upload'},
        'post_params': {'description': 'POST 参数名', 'placeholder': '请填写file'},
        'json_path': {'description': 'JSON 路径', 'placeholder': '请填写0.src'},
        'api_key': {'description': 'API 密钥', 'placeholder': '例如：imgbed_XXXXXXXXX'},
        'custom_url': {'description': '自定义前缀', 'placeholder': '例如：https://example.com'},
        'delete_url': {'description': '删除 API 地址', 'placeholder': '例如：https://example.com/api/manage/delete'},
        'upload_folder': {'description': '上传的文件夹', 'placeholder': '图床保存的文件夹'},
        'upload_name_type': {'description': '文件命名规则', 'placeholder': '可选：default, index, origin, short (默认: default)'}
    }

    def __init__(self, api, post_params, json_path, api_key, custom_url, delete_url, upload_folder="", upload_name_type="default"):
        self.api = api
        self.post_params = post_params
        self.json_path = json_path
        self.api_key = api_key
        self.custom_url = custom_url
        self.delete_url = delete_url
        self.upload_folder = upload_folder
        self.upload_name_type = upload_name_type

    def upload(self, file):
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        # 使用 requests 的 params 参数构造并编码查询参数，避免手写字符串拼接
        params = {}
        if self.upload_folder:
            folder_path = replace_folder_path(self.upload_folder)
            params["uploadFolder"] = folder_path

        if self.upload_name_type:
            params["uploadNameType"] = self.upload_name_type

        response = requests.post(
            self.api,
            headers=headers,
            params=params or None,
            files={self.post_params: [file.name, file.read(), file.content_type]},
        )
        data = response.text
        logging.info(data)
        if self.json_path:
            json_path = self.json_path.split(".")
            response.encoding = "utf8"
            url = json.loads(data)
            for path in json_path:
                if isinstance(url, list):  # 处理列表Index
                    url = url[int(path)]
                else:
                    url = url[path]
        else:
            url = data
            
        if self.delete_url:
            # Remove trailing slash from delete_url or leading slash from url to avoid double slashes
            d_url = self.delete_url if self.delete_url.endswith('/') else self.delete_url + '/'
            d_path = str(url)
            
            if d_path.startswith('/file/'):
                d_path = d_path[6:]
            elif d_path.startswith('/file'):
                d_path = d_path[5:]
                
            d_path = d_path.lstrip('/')
            delete_full_url = d_url + d_path
            
            return [str(self.custom_url) + str(url), {"provider": Main.name, "delete_url": delete_full_url, "api_key": self.api_key}]

        # 当未配置 delete_url 时，不返回删除配置，避免后续删除时因缺少 delete_url 失败
        return [str(self.custom_url) + str(url), {}]
