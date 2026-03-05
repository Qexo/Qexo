"""
@Project   : cfimgbed
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

import json
import requests
import logging

from ..core import Provider
from ..replace import replace_path


def delete(config):
    response = requests.get(config.get("delete_url"))
    return response.text


class Main(Provider):
    name = 'CFImgBed'

    params = {
        'api': {'description': 'API 地址', 'placeholder': '图床图片上传的 API，例如：https://example.com/upload'},
        'post_params': {'description': 'POST 参数名', 'placeholder': '图床图片上传 API 参数中图片文件的参数名'},
        'json_path': {'description': 'JSON 路径', 'placeholder': '返回数据中图片 URL 所在的路径'},
        'api_key': {'description': 'API 密钥', 'placeholder': '例如：imgbed_XXXXXXXXX'},
        'custom_url': {'description': '自定义前缀', 'placeholder': '返回 URL 所需要添加的前缀'},
        'delete_url': {'description': '删除 API 地址', 'placeholder': '例如：https://example.com/api/delete/'},
        'upload_folder': {'description': '上传的文件夹', 'placeholder': '图床保存的文件夹，支持 {YYYY} {MM} 等通配符'},
        'upload_name_type': {'description': '命名规则', 'placeholder': '可选：default, index, origin, short (默认: default)'}
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
            
        upload_api_url = self.api
        
        # Prepare query parameters
        query_params = []
        if self.upload_folder:
            folder_path = replace_path(self.upload_folder)
            query_params.append(f"uploadFolder={folder_path}")

        if self.upload_name_type:
            query_params.append(f"uploadNameType={self.upload_name_type}")
            
        if query_params:
            if '?' in upload_api_url:
                if not upload_api_url.endswith('?'):
                    upload_api_url += "&"
                upload_api_url += "&".join(query_params)
            else:
                upload_api_url += "?" + "&".join(query_params)
            
        response = requests.post(upload_api_url, headers=headers,
                                 files={self.post_params: [file.name, file.read(),
                                                           file.content_type]})
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
            d_path = str(url).lstrip('/')
            delete_full_url = d_url + d_path
            
            return [str(self.custom_url) + str(url), {"provider": Main.name, "delete_url": delete_full_url}]

        return [str(self.custom_url) + str(url), {}]
