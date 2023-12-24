"""
@Project   : github
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

import github
from datetime import datetime
from hashlib import md5

from ..core import Provider
from ..replace import replace_path


class Github(Provider):
    name = "Github"

    def __init__(self, token, repo, branch, path, url):
        self.token = token
        self._repo = repo
        self.branch = branch
        self.path = path
        self.url = url
        self.repo = github.Github(self.token).get_repo(self._repo)

    params = {
        'token': {"description": "Github 密钥", "placeholder": "token"},
        'repo': {"description": "Github 仓库", "placeholder": "username/repo"},
        'branch': {"description": "项目分支", "placeholder": "e.g. master"},
        'path': {'description': '保存路径', 'placeholder': '文件上传后保存的路径 包含文件名'},
        'url': {'description': '自定义域名', 'placeholder': '需填写完整路径'}
    }

    def upload(self, file):
        now = datetime.now()
        photo_stream = file.read()
        file_md5 = md5(photo_stream).hexdigest()
        path = replace_path(self.path, file, file_md5, now)

        commitchange = "Upload {} by Qexo".format(file.name)
        try:
            self.repo.update_file(path, commitchange, photo_stream,
                                  self.repo.get_contents(self.path + path, ref=self.branch).sha, branch=self.branch)
        except:
            self.repo.create_file(path, commitchange, photo_stream, branch=self.branch)

        return replace_path(self.url, file, file_md5, now)
