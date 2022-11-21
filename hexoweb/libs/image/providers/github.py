import github

from ..core import Provider


class Github(Provider):

    def __init__(self, repo, branch, path):
        try:
            from hexoweb.functions import _Provider
        except Exception:
            raise Exception("未配置 Github Token")
        self._repo = repo
        self.repo = github.Github(_Provider.token).get_repo(self._repo)
        self.branch = branch
        self.path = path if not str(path).startswith('/') else str(path)[1:]
        self.path = self.path if self.path.endswith("/") else self.path + "/"

    def save(self, file, content, commit_change="Upload img by Qexo"):
        self.repo.create_file(self.path + file, commit_change, content, branch=self.branch)
        print("保存文件{}成功".format(file))
        return True

    # noinspection DuplicatedCode
    def delete(self, path, commit_change="Delete img by Qexo"):
        file = self.repo.get_contents(self.path + path, ref=self.branch)
        if not isinstance(file, list):
            self.repo.delete_file(self.path + path, commit_change, file.sha, branch=self.branch)
        else:
            for i in file:
                self.repo.delete_file(self.path + i.path, commit_change, i.sha, branch=self.branch)
        return True

    name = 'Github'
    params = {
        'repo': {"description": "Github 仓库", "placeholder": "username/repo"},
        'branch': {"description": "项目分支", "placeholder": "分支"},
        'path': {"description": "存储路径", "placeholder": "留空为根目录"}
    }

    def upload(self, file):
        img_data = bytearray(file.read())
        if self.save(file.name, bytes(img_data)):
            return "https://cdn.jsdelivr.net/gh/" + self.repo.full_name + "/" + self.path + file.name

    def del_img(self, file_name):
        self.delete(file_name)
