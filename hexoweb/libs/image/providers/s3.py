"""
@Project   : s3
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

import boto3
from hashlib import md5
from datetime import datetime

from ..core import Provider
from ..replace import replace_path


def delete(config):
    s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=config.get("key_id"),
        aws_secret_access_key=config.get("access_key"),
        endpoint_url=config.get("endpoint_url"),
        region_name=config.get("region_name"),
        verify=False
    )
    s3.Object(config.get("bucket"), config.get("path")).delete()
    return "删除成功"


class Main(Provider):
    name = 'S3协议'
    params = {
        'key_id': {'description': '应用密钥 ID', 'placeholder': 'S3 应用程序的 Access Key ID'},
        'access_key': {'description': '应用秘钥', 'placeholder': 'S3 应用程序的 Access Key'},
        'bucket': {'description': '储存桶名', 'placeholder': 'S3 Bucket 名称'},
        'endpoint_url': {'description': '边缘节点', 'placeholder': 'S3 Endpoint'},
        'region_name': {'description': '地区', 'placeholder': 'S3 Endpoint 区域'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '需填写完整路径'}
    }

    def __init__(self, key_id, access_key, endpoint_url, region_name, bucket, path, prev_url):
        self.key_id = key_id
        self.access_key = access_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.bucket = bucket
        self.path = path
        self.prev_url = prev_url

    def upload(self, file):
        now = datetime.now()
        photo_stream = file.read()
        file_md5 = md5(photo_stream).hexdigest()
        path = replace_path(self.path, file, file_md5, now)

        s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.access_key,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            verify=False,
        )
        bucket = s3.Bucket(self.bucket)
        bucket.put_object(Key=path, Body=photo_stream, ContentType=file.content_type)

        delete_config = {
            "provider": Main.name,
            "key_id": self.key_id,
            "access_key": self.access_key,
            "endpoint_url": self.endpoint_url,
            "region_name": self.region_name,
            "bucket": self.bucket,
            "path": path
        }

        return [replace_path(self.prev_url, file, file_md5, now), delete_config]
