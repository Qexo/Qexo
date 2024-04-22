"""
@Project   : upyun
@Author    : admsec & abudu
@Blog      : https://www.admsec.top & https://www.oplog.cn
"""

import boto3
from hashlib import md5
from datetime import datetime

import upyun

from ..core import Provider
from ..replace import replace_path


def upyun_api(service, username, password):
    up = upyun.UpYun(service, username=username, password=password)
    return up


def delete(config):
    service = config.get('service')
    username = config.get('username')
    password = config.get('password')
    path = config.get('path')
    up = upyun_api(service, username, password)
    try:
        up.delete(path)
    except:
        raise Exception("upyun_storage.py: delete error")
    return "删除成功"


class Main(Provider):
    name = '又拍云-云储存'
    params = {
        'service': {'description': 'bucket名称', 'placeholder': '云储存里的服务名称'},
        'username': {'description': '操作员名', 'placeholder': '又拍云的操作员名'},
        'password': {'description': '操作员密码', 'placeholder': '又拍云的操作员密码'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '需填写完整路径'}
    }

    def __init__(self, service, username, password, path, prev_url):
        self.service = service
        self.username = username
        self.password = password
        self.path = path
        self.prev_url = prev_url

    def upload(self, file):
        now = datetime.now()
        photo_stream = file.read()
        file_md5 = md5(photo_stream).hexdigest()
        path = replace_path(self.path, file, file_md5, now)

        # 上传操作
        try:
            up = upyun_api(self.service, self.username, self.password)
            up.put(path, photo_stream)
        except:
            raise Exception("upyun_storage.py: upload error")

        delete_config = {
            "provider": Main.name,
            "service": self.service,
            "username": self.username,
            "password": self.password,
            "path": path
        }

        return [replace_path(self.prev_url, file, file_md5, now), delete_config]
