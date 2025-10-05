import gitlab
from ..core import Provider
import logging

class Gitlab(Provider):
    name = "gitlab"

    def __init__(self, url, token, repo, branch, path, config):
        super(Gitlab, self).__init__(config)
        self.url = url
        self.token = token
        self._repo = repo
        self.branch = branch
        self.path = path if path != "/" else ""
        self.repo = (gitlab.Gitlab(url=url, private_token=token) if url else gitlab.Gitlab(private_token=token)).projects.get(repo)

    params = {'url': {"description": "Gitlab 地址", "placeholder": "留空为官网"},
              'token': {"description": "Gitlab 密钥", "placeholder": "token"},
              'repo': {"description": "Gitlab 仓库", "placeholder": "username/repo"},
              'branch': {"description": "项目分支", "placeholder": "e.g. master"},
              'path': {"description": "博客路径", "placeholder": "留空为根目录"}}

    def get_content(self, file):  # 获取文件内容UTF8
        logging.info("获取文件{}".format(file))
        content = self.repo.files.get(self.path + file, ref=self.branch).decode().decode("utf8")
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
        contents = self.repo.repository_tree(path[:-1] if path.endswith("/") else path, ref=self.branch, get_all=True)
        for file in contents:
            if file["type"] == "blob":
                results.append({
                    "name": file["name"],
                    "size": 0,
                    "path": file["path"] if not file["path"].startswith(self.path) else file["path"][len(self.path):],
                    "type": "file"
                })
            if file["type"] == "tree":
                results.append({
                    "name": file["name"],
                    "path": file["path"] if not file["path"].startswith(self.path) else file["path"][len(self.path):],
                    "type": "dir"
                })
        logging.info("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def save(self, file, content, commitchange="Update by Qexo", autobuild=True):
        try:
            f = self.repo.files.create({'file_path': self.path + file,
                          'branch': self.branch,
                          'content': content,
                          'commit_message': commitchange})
            logging.info("新建文件{}成功".format(file))
        except:
            f = self.repo.files.get(file_path=self.path + file, ref=self.branch)
            f.content = content
            f.save(branch=self.branch, commit_message=commitchange)
            logging.info("保存文件{}成功".format(file))
        return False

    def delete(self, path, commitchange="Delete by Qexo", autobuild=True):
        try:
            file = self.repo.files.get(file_path=self.path + path, ref=self.branch)
            file.delete(commit_message=commitchange, branch=self.branch)
            logging.info("删除文件{}成功".format(path))
        except:
            tree = self.get_path(self.path + path)
            for i in tree["data"]:
                self.delete(i["path"][len(self.path):], commitchange=commitchange)
            logging.info("删除目录{}成功".format(path))
        return False

    def get_tree(self, path, depth, exclude=None):
        """
        Use GitLab API to fetch directory tree via repository_tree endpoint.
        """
        if not depth:
            return {"path": path, "data": []}
        if exclude is None:
            exclude = []
        # normalize prefix without trailing slash
        prefix = (self.path + path).rstrip('/')
        # fetch full tree recursively
        tree = self.repo.repository_tree(path=prefix, ref=self.branch, recursive=True, get_all=True)
        results = []
        for element in tree:
            p = element.get('path')
            # filter by prefix
            if prefix:
                if not p.startswith(prefix + '/'):
                    continue
                rel = p[len(prefix) + 1:]
            else:
                rel = p
            parts = rel.split('/') if rel else []
            # respect depth
            # if parts and len(parts) - len(path.split("/")) > depth: # no depth respect is a feature
            #     continue
            # filter excludes
            if exclude and any(seg in exclude for seg in parts):
                continue
            name = parts[-1] if parts else ''
            typ = 'file' if element.get('type') == 'blob' else 'dir'
            item = {"name": name,
                    "path": p[len(self.path):] if p.startswith(self.path) else p,
                    "type": typ}
            if typ == 'file':
                item['size'] = 0
            results.append(item)
        return results
