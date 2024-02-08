"""
@Project   : dogecloudoss
@Author    : tianxiang_tnxg & Abudu
@Blog      : https://tnxg.loyunet.cn & https://www.oplog.cn
"""

from datetime import datetime
import boto3
from hashlib import md5
from hashlib import sha1
import hmac
import requests
import json

from ..core import Provider
from ..replace import replace_path


def dogecloud_api(access_key, secret_key):
    access_key = access_key
    secret_key = secret_key
    api_path = "/auth/tmp_token.json"
    data = {'channel': 'OSS_FULL', 'scopes': ['*']}
    body = json.dumps(data)
    mime = 'application/json'
    sign_str = api_path + "\n" + body
    signed_data = hmac.new(secret_key.encode(
        'utf-8'), sign_str.encode('utf-8'), sha1)
    sign = signed_data.digest().hex()
    authorization = 'TOKEN ' + access_key + ':' + sign
    response = requests.post('https://api.dogecloud.com' + api_path, data=body, headers={
        'Authorization': authorization,
        'Content-Type': mime
    })
    return response.json()


def delete(config):
    access_key = config.get("access_key")
    secret_key = config.get("secret_key")
    endpoint_url = config.get("endpoint_url")
    bucket = config.get("bucket")
    path = config.get("path")
    res = dogecloud_api(access_key, secret_key)
    if res['code'] != 200:
        raise Exception("Api failed: " + res['msg'])
    credentials = res['data']['Credentials']
    s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=credentials['accessKeyId'],
        aws_secret_access_key=credentials['secretAccessKey'],
        aws_session_token=credentials['sessionToken'],
        endpoint_url=endpoint_url,
    )
    bucket = s3.Bucket(bucket)
    bucket.delete_object(Key=path)
    return "删除成功"


class Main(Provider):
    name = 'DogeCloud云存储'
    params = {
        'access_key': {'description': 'DogeCloud_Accesskey', 'placeholder': 'DogeCloud用户的Accesskey'},
        'secret_key': {'description': 'DogeCloud_Secretkey', 'placeholder': 'DogeCloud用户的Secretkey'},
        'bucket': {'description': '储存桶名', 'placeholder': 'DogeCloud 储存桶 (Bucket) 名称'},
        'endpoint_url': {'description': '边缘节点', 'placeholder': 'DogeCloud Endpoint'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '需填写完整路径'}
    }

    def __init__(self, secret_key, access_key, endpoint_url, bucket, path, prev_url):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.path = path
        self.prev_url = prev_url

    def upload(self, file):
        now = datetime.now()
        photo_stream = file.read()
        file_md5 = md5(photo_stream).hexdigest()
        path = replace_path(self.path, file, file_md5, now)

        res = dogecloud_api(self.access_key, self.secret_key)
        if res['code'] != 200:
            raise Exception("Api failed: " + res['msg'])
        credentials = res['data']['Credentials']

        s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=credentials['accessKeyId'],
            aws_secret_access_key=credentials['secretAccessKey'],
            aws_session_token=credentials['sessionToken'],
            endpoint_url=self.endpoint_url,
        )
        bucket = s3.Bucket(self.bucket)
        bucket.put_object(Key=path, Body=photo_stream,
                          ContentType=file.content_type)

        delete_config = {
            "provider": Main.name,
            "access_key": self.access_key,
            "secret_key": self.secret_key,
            "endpoint_url": self.endpoint_url,
            "bucket": self.bucket,
            "path": path
        }

        return [replace_path(self.prev_url, file, file_md5, now), delete_config]
