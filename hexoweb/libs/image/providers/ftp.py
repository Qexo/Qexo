"""
@Project   : ftp
@Author    : abudu
@Blog      : https://www.oplog.cn
"""
import ftplib
from ftplib import FTP
from datetime import datetime
import os
from hashlib import md5

from ..core import Provider
from ..replace import replace_path


def create_dir(ftp, path):
    try:
        ftp.cwd(path)
    except ftplib.all_errors as e:
        create_dir(ftp, os.path.dirname(path))
        ftp.mkd(path)


def delete(config):
    ftp = FTP(encoding=config.get("encoding"))
    ftp.connect(config.get("host"), int(config.get("port")))
    ftp.login(config.get("user"), config.get("password"))
    ftp.delete(config.get("path"))
    ftp.quit()
    return "删除成功"


class Main(Provider):
    name = 'FTP协议'
    params = {
        'host': {'description': 'FTP 主机', 'placeholder': '所连接的 FTP 主机'},
        'port': {'description': 'FTP 端口', 'placeholder': 'FTP 连接端口 通常为 21'},
        'user': {'description': '用户名', 'placeholder': 'FTP 登录用户名'},
        'password': {'description': '密码', 'placeholder': 'FTP 登录密码'},
        'encoding': {'description': 'FTP 编码', 'placeholder': '如 utf-8/gbk'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '需填写完整路径'}
    }

    def __init__(self, host, port, user, password, path, prev_url, encoding="utf-8"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.path = path
        self.prev_url = prev_url
        self.encoding = encoding

    def upload(self, file):
        ftp = FTP(encoding=self.encoding)
        ftp.set_debuglevel(0)
        ftp.connect(self.host, int(self.port))
        ftp.login(self.user, self.password)
        now = datetime.now()
        photo_stream = file.read()
        file_md5 = md5(photo_stream).hexdigest()
        file.file.seek(0)  # seek file
        path = replace_path(self.path, file, file_md5, now)
        bufsize = 1024
        try:
            ftp.storbinary('STOR ' + path, file, bufsize)
        except ftplib.all_errors as e:
            create_dir(ftp, os.path.dirname(path))
            ftp.storbinary('STOR ' + path, file, bufsize)
        ftp.quit()

        delete_config = {
            "provider": Main.name,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "encoding": self.encoding,
            "path": path
        }

        return [replace_path(self.prev_url, file, file_md5, now), delete_config]
