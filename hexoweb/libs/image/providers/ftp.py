"""
@Project   : ftp
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

from ftplib import FTP
from time import time
from datetime import date

from ..core import Provider


class Ftp(Provider):
    name = 'FTP协议'
    params = {
        'host': {'description': 'FTP 主机', 'placeholder': '所连接的 FTP 主机'},
        'port': {'description': 'FTP 端口', 'placeholder': 'FTP 连接端口 通常为 21'},
        'user': {'description': '用户名', 'placeholder': 'FTP 登录用户名'},
        'password': {'description': '密码', 'placeholder': 'FTP 登录密码'},
        'encoding': {'description': 'FTP 编码', 'placeholder': '如 utf-8/gbk'},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'prev_url': {'description': '自定义域名', 'placeholder': '最终返回的链接为自定义域名+保存路径'}
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
        now = date.today()
        path = self.path.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}",
                                                                                                     str(now.day)) \
            .replace("{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{time}", str(time())) \
            .replace("{extName}", file.name.split(".")[-1])
        bufsize = 1024
        ftp.storbinary('STOR ' + path, file, bufsize)
        return self.prev_url.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}",
                                                                                                         str(now.day)) \
            .replace("{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{time}", str(time())) \
            .replace("{extName}", file.name.split(".")[-1])
