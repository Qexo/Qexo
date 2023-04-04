"""
@Project   : Ali OSS
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

from datetime import date
import oss2
from time import time
from hashlib import md5

from ..core import Provider


class AliOss(Provider):
    name = '阿里云OSS'
    params = {
        'access_id': {'description': '应用密钥 ID', 'placeholder': 'RAM用户/阿里云账号AccessKey ID'},
        'access_key': {'description': '应用秘钥', 'placeholder': 'RAM用户/阿里云账号AccessKey'},
        'bucket': {'description': '储存桶名', 'placeholder': '存储桶名称'},
        'endpoint_url': {'description': '边缘节点', 'placeholder': '所在地域对应的Endpoint'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '最终返回的链接为自定义域名/保存路径'}
    }

    def __init__(self, access_id, access_key, endpoint_url, bucket, path, prev_url):
        self.access_id = access_id
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
        # 处理路径开头斜杠
        path = path[1:] if path.startswith("/") else path

        # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
        auth = oss2.Auth(self.access_id, self.access_key)
        # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
        # 填写Bucket名称。
        bucket = oss2.Bucket(auth, self.endpoint_url, self.bucket)

        bucket.put_object(path, photo_stream, headers={"Content-Type": file.content_type})

        return self.prev_url.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}", str(now.day)).replace(
            "{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{extName}", file.name.split(".")[-1]).replace(
            "{md5}", file_md5)
