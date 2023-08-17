import github
from ..core import Provider
import logging


class Github(Provider):
    name = "github"

    def __init__(self, token, repo, branch, path, config):
        super(Github, self).__init__(config)
        self.token = token
        self._repo = repo
        self.branch = branch
        self.path = path if path != "/" else ""
        self.repo = github.Github(self.token).get_repo(self._repo)

    params = {'token': {"description": "Github 密钥", "placeholder": "token"},
              'repo': {"description": "Github 仓库", "placeholder": "username/repo"},
              'branch': {"description": "项目分支", "placeholder": "e.g. master"},
              'path': {"description": "博客路径", "placeholder": "留空为根目录"}}

    def get_content(self, file):  # 获取文件内容UTF8
        logging.info("获取文件{}".format(file))
        content = self.repo.get_contents(self.path + file, self.branch).decoded_content.decode("utf8")
        return content

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
        contents = self.repo.get_contents(path[:-1] if path.endswith("/") else path, self.branch)
        for file in contents:
            if file.type == "file":
                results.append({
                    "name": file.name,
                    "size": file.size,
                    "path": file.path if not file.path.startswith(self.path) else file.path[len(self.path):],
                    "type": file.type
                })
            if file.type == "dir":
                results.append({
                    "name": file.name,
                    "path": file.path if not file.path.startswith(self.path) else file.path[len(self.path):],
                    "type": file.type
                })
        logging.info("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def save(self, file, content, commitchange="Update by Qexo", autobuild=True):
        try:
            self.repo.update_file(self.path + file, commitchange, content,
                                  self.repo.get_contents(self.path + file, ref=self.branch).sha, branch=self.branch)
            logging.info("保存文件{}成功".format(file))
        except:
            self.repo.create_file(self.path + file, commitchange, content, branch=self.branch)
            logging.info("新建文件{}成功".format(file))
        return False  # 返回False表示没有进行自动部署

    def delete(self, path, commitchange="Delete by Qexo", autobuild=True):
        file = self.repo.get_contents(self.path + path, ref=self.branch)
        if not isinstance(file, list):
            self.repo.delete_file(self.path + path, commitchange, file.sha, branch=self.branch)
            logging.info("删除文件{}成功".format(path))
        else:
            for i in file:
                self.delete(i.path[len(self.path):], commitchange)
            logging.info("删除目录{}成功".format(path))
        return False

    def delete_hooks(self):
        for hook in self.repo.get_hooks():  # 删除所有HOOK
            hook.delete()
        logging.info("删除所有WebHook成功")
        return True

    def create_hook(self, config):
        self.repo.create_hook(active=True, config=config, events=["push"], name="web")
        logging.info("创建WebHook成功{}".format(config))
        return True
