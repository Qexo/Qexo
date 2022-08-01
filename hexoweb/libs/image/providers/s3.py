"""
@Project   : s3
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

from datetime import date
import boto3
from time import time
from hashlib import md5

from ..core import Provider


class S3(Provider):
    name = 'S3协议'
    params = {
        'key_id': {'description': '应用密钥 ID', 'placeholder': 'S3 应用程序的 Access Key ID'},
        'access_key': {'description': '应用秘钥', 'placeholder': 'S3 应用程序的 Access Key'},
        'bucket': {'description': '储存桶名', 'placeholder': 'S3 Bucket 名称'},
        'endpoint_url': {'description': '边缘节点', 'placeholder': 'S3 Endpoint'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '最终返回的链接为自定义域名/保存路径'}
    }

    def __init__(self, key_id, access_key, endpoint_url, bucket, path, prev_url):
        self.key_id = key_id
        self.access_key = access_key
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.path = path
        self.prev_url = prev_url

    def upload(self, file):
        now = date.today()
        photo_stream = file.read()
        file_md5 = md5(photo_stream).hexdigest()
        path = self.path.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}", str(now.day)).replace(
            "{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{extName}", file.name.split(".")[-1]).replace("{md5}",
                                                                                                                                  file_md5)

        s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.access_key,
            endpoint_url=self.endpoint_url,
            verify=False,
        )
        bucket = s3.Bucket(self.bucket)
        bucket.put_object(Key=path, Body=photo_stream, ContentType=file.content_type)

        return self.prev_url.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}", str(now.day)).replace(
            "{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{extName}", file.name.split(".")[-1]).replace(
            "{md5}", file_md5)
