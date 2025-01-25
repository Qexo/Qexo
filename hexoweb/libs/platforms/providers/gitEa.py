import requests
from ..core import Provider
import base64
import logging


class GitEa(Provider):
    name = "gitea"

    def __init__(self, url, token, repo, branch, path, config):
        super(GitEa, self).__init__(config)
        self.url = url + "api/v1" if url.endswith("/") else url + "/api/v1"
        self.token = token
        self.repo = repo
        self.branch = branch
        self.path = path if path != "/" else ""

    params = {'url': {"description": "Gitea 地址", "placeholder": "https://git.example.com"},
              'token': {"description": "Gitea 密钥", "placeholder": "token"},
              'repo': {"description": "Gitea 仓库", "placeholder": "username/repo"},
              'branch': {"description": "项目分支", "placeholder": "e.g. master"},
              'path': {"description": "博客路径", "placeholder": "留空为根目录"}}

    def request(self, url, method, data=None):
        url = self.url + url
        headers = {
            "Authorization": "token " + self.token,
            "Content-Type": "application/json"
        }
        if method == "GET":
            res = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            res = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            res = requests.delete(url, headers=headers, json=data)
        else:
            raise Exception("Method not allowed")
        if not str(res.status_code).startswith("2"):
            raise Exception("Request failed: {}".format(res.text))
        return res

    def get_content(self, file):  # 获取文件内容UTF8
        logging.info("获取文件{}".format(file))
        url = "/repos/" + self.repo + "/media/" + self.path + file
        return self.request(url, "GET").text

    def get_path(self, path):  # 获取目录下的文件列表
        """
        :param path: 目录路径
        :return: {
            "data":[{"type":"dir/file", "name":"文件名", "path":"文件路径", "size":"文件大小(仅文件)"}, ...],
            "path":"当前路径"
            }
        """
        results = list()
        path = self.path + path
        url = "/repos/" + self.repo + "/contents/" + path
        contents = self.request(url, "GET", data={"ref": self.branch}).json()
        for file in contents:
            if file["type"] == "file":
                results.append({
                    "name": file["name"],
                    "size": file["size"],
                    "path": file["path"] if not file["path"].startswith(self.path) else file["path"][len(self.path):],
                    "type": "file"
                })
            if file["type"] == "dir":
                results.append({
                    "name": file["name"],
                    "path": file["path"] if not file["path"].startswith(self.path) else file["path"][len(self.path):],
                    "type": "dir"
                })
        logging.info("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def save(self, file, content, commitchange="Update by Qexo", autobuild=True):
        content = base64.b64encode(content.encode()).decode()
        try:
            url = "/repos/" + self.repo + "/contents/" + self.path + file
            data = {'branch': self.branch,
                    'content': content,
                    'message': commitchange}
            self.request(url, "POST", data).json()
            logging.info("新建文件{}成功".format(file))
        except:
            url = "/repos/" + self.repo + "/contents/" + self.path + file
            data = {'branch': self.branch,
                    'content': content,
                    'sha': self.request("/repos/" + self.repo + "/contents/" + self.path + file, "GET").json()["sha"],
                    'message': commitchange}
            self.request(url, "PUT", data)
            logging.info("保存文件{}成功".format(file))
        return False

    def delete(self, path, commitchange="Delete by Qexo", autobuild=True):
        file = self.request("/repos/" + self.repo + "/contents/" + self.path + path, "GET").json()
        if type(file) == list:
            tree = self.get_path(self.path + path)
            for i in tree["data"]:
                self.delete(i["path"][len(self.path):], commitchange=commitchange)
            logging.info("删除目录{}成功".format(path))
        else:
            url = "/repos/" + self.repo + "/contents/" + self.path + path
            data = {'branch': self.branch,
                    'sha': file["sha"],
                    'message': commitchange}
            self.request(url, "DELETE", data)
            logging.info("删除文件{}成功".format(path))
        return False

    def delete_hooks(self):
        for hook in self.request("/repos/" + self.repo + "/hooks", "GET").json():  # 删除所有HOOK
            self.request("/repos/" + self.repo + "/hooks/" + str(hook["id"]), "DELETE")
        logging.info("删除所有WebHook成功")
        return True

    def create_hook(self, uri):
        url = "/repos/" + self.repo + "/hooks"
        data = {
            "active": True,
            "description": "Qexo WebHook",
            "type": "gitea",
            "config": {
                "content_type": "json",
                "url": uri
            },
            "events": ["push"]
        }
        self.request(url, "POST", data)
        logging.info("创建WebHook成功{}".format(data["config"]))
        return True
