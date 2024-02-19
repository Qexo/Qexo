"""
@Project   : custom
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

import json
import requests
import logging

from ..core import Provider


def delete(config):
    response = requests.get(config.get("delete_url"))
    return response.text


class Main(Provider):
    name = '远程API'

    params = {
        'api': {'description': 'API 地址', 'placeholder': '图床图片上传的 API'},
        'post_params': {'description': 'POST 参数名', 'placeholder': '图床图片上传 API 参数中图片文件的参数名'},
        'json_path': {'description': 'JSON 路径', 'placeholder': '返回数据中图片 URL 所在的路径'},
        'custom_header': {'description': '自定义请求头', 'placeholder': '[JSON]POST 请求时额外的请求头'},
        'custom_body': {'description': '自定义请求主体', 'placeholder': '[JSON]POST 请求时额外的请求主体'},
        'custom_url': {'description': '自定义前缀', 'placeholder': '返回 URL 所需要添加的前缀'},
        'delete_url': {'description': '删除 API', 'placeholder': '图床图片删除的 API (填写 JSON 路径)'}
    }

    def __init__(self, api, post_params, json_path, custom_body, custom_header, custom_url, delete_url):
        self.api = api
        self.post_params = post_params
        self.json_path = json_path
        self.custom_body = custom_body
        self.custom_header = custom_header
        self.custom_url = custom_url
        self.delete_url = delete_url

    def upload(self, file):
        if self.custom_header:
            if self.custom_body:
                response = requests.post(self.api, data=json.loads(self.custom_body),
                                         headers=json.loads(self.custom_header),
                                         files={self.post_params: [file.name, file.read(),
                                                                   file.content_type]})
            else:
                response = requests.post(self.api, data={}, headers=json.loads(self.custom_header),
                                         files={self.post_params: [file.name, file.read(),
                                                                   file.content_type]})
        else:
            if self.custom_body:
                response = requests.post(self.api, data=json.loads(self.custom_body),
                                         files={self.post_params: [file.name, file.read(),
                                                                   file.content_type]})
            else:
                response = requests.post(self.api, data={},
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
            json_path = self.delete_url.split(".")
            delete_url = json.loads(data)
            for path in json_path:
                if isinstance(url, list):
                    delete_url = delete_url[int(path)]
                else:
                    delete_url = delete_url[path]
            return [str(self.custom_url) + str(url), {"provider": Main.name, "delete_url": delete_url}]

        return [str(self.custom_url) + str(url), {}]
