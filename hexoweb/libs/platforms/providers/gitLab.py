import gitlab
from ..core import Provider


class Gitlab(Provider):
    name = "gitlab"

    def __init__(self, url, token, repo, branch, path):
        self.url = url
        self.token = token
        self._repo = repo
        self.branch = branch
        self.path = path
        self.repo = (gitlab.Gitlab(url=url, private_token=token) if url else gitlab.Gitlab(private_token=token)).projects.get(repo)

    params = {'url': {"description": "Gitlab 地址", "placeholder": "留空为官网"},
              'token': {"description": "Gitlab 密钥", "placeholder": "token"},
              'repo': {"description": "Gitlab 仓库", "placeholder": "username/repo"},
              'branch': {"description": "项目分支", "placeholder": "e.g. master"},
              'path': {"description": "Hexo 路径", "placeholder": "留空为根目录"}}

    def get_content(self, file):  # 获取文件内容UTF8
        print("获取文件{}".format(file))
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
        contents = self.repo.repository_tree(self.path + path, ref=self.branch)
        for file in contents:
            if file["type"] == "blob":
                results.append({
                    "name": file["name"],
                    "size": 0,
                    "path": file["path"],
                    "type": "file"
                })
            if file["type"] == "tree":
                results.append({
                    "name": file["name"],
                    "path": file["path"],
                    "type": "dir"
                })
        print("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def save(self, file, content, commitchange="Update by Qexo"):
        try:
            f = self.repo.files.create({'file_path': self.path + file,
                          'branch': self.branch,
                          'content': content,
                          'commit_message': commitchange})
            print("新建文件{}成功".format(file))
        except:
            f = self.repo.files.get(file_path=self.path + file, ref=self.branch)
            f.content = content
            f.save(branch=self.branch, commit_message=commitchange)
            print("保存文件{}成功".format(file))
        return False

    def delete(self, path, commitchange="Delete by Qexo"):
        try:
            file = self.repo.files.get(file_path=self.path + path, ref=self.branch)
            file.delete(commit_message=commitchange, branch=self.branch)
            print("删除文件{}成功".format(path))
        except:
            tree = self.get_path(self.path + path)
            for i in tree["data"]:
                self.delete(i["path"][len(self.path):], commitchange=commitchange)
            print("删除目录{}成功".format(path))
        return False
