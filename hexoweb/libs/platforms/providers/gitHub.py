import github
from ..core import Provider


class Github(Provider):
    name = "github"

    def __init__(self, token, repo, branch, path):
        self.token = token
        self._repo = repo
        self.branch = branch
        self.path = path
        self.repo = github.Github(self.token).get_repo(self._repo)

    params = {'token': {"description": "Github 密钥", "placeholder": "token"},
              'repo': {"description": "Github 仓库", "placeholder": "username/repo"},
              'branch': {"description": "项目分支", "placeholder": "master"},
              'path': {"description": "Hexo 路径", "placeholder": "留空为根目录"}}

    def get_post(self, post):
        try:
            content = self.repo.get_contents(self.path + "source/_drafts/" + post,
                                             self.branch).decoded_content.decode("utf8")
            print("从草稿中获取文章{}成功".format(post))
        except:
            content = self.repo.get_contents(self.path + "source/_posts/" + post,
                                             self.branch).decoded_content.decode("utf8")
            print("获取文章{}成功".format(post))
        return content

    def get_content(self, file):
        print("获取文件{}".format(file))
        content = self.repo.get_contents(self.path + file, self.branch).decoded_content.decode("utf8")
        return content

    def get_path(self, path):
        results = list()
        contents = self.repo.get_contents(self.path + path, self.branch)
        for file in contents:
            if file.type == "file":
                results.append({
                    "name": file.name,
                    "size": file.size,
                    "type": file.type
                })
            else:
                results.append({
                    "name": file.name,
                    "type": file.type
                })
        print("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def get_posts(self, _path=""):
        _posts = list()
        _drafts = list()
        names = list()
        try:
            drafts = self.repo.get_contents(self.path + 'source/_drafts' + _path,
                                            ref=self.branch)
            for i in range(len(drafts)):
                if drafts[i].type == "file" and drafts[i].name[-2:] == "md":
                    _drafts.append({"name": drafts[i].path.split(
                        "source/_drafts/")[1][0:-3], "fullname": drafts[i].path.split(
                        "source/_drafts/")[1],
                                    "path": drafts[i].path,
                                    "size": drafts[i].size, "status": False})
                    names.append(drafts[i].path.split("source/_drafts/")[1])
                if drafts[i].type == "dir":
                    dir_content = self.get_posts(_path=drafts[i].path.split("source/_drafts")[1])
                    for file in dir_content:
                        if "source/_drafts" in file["path"]:
                            _drafts.append(file)
                            names.append(file["fullname"])
        except:
            pass
        try:
            posts = self.repo.get_contents(self.path + 'source/_posts' + _path, ref=self.branch)
            for i in range(len(posts)):
                if posts[i].type == "file" and posts[i].name[-2:] == "md":
                    if posts[i].path.split(
                            "source/_posts/")[1] not in names:
                        _posts.append(
                            {"name": posts[i].path.split("source/_posts/")[1][0:-3],
                             "fullname": posts[i].path.split("source/_posts/")[1],
                             "path": posts[i].path,
                             "size": posts[i].size,
                             "status": True})

                if posts[i].type == "dir":
                    dir_content = self.get_posts(_path=posts[i].path.split("source/_posts")[1])
                    for file in dir_content:
                        if ("source/_posts" in file["path"]) and (file["fullname"] not in names):
                            _posts.append(file)
                            names.append(file["fullname"])
        except:
            pass
        posts = _posts + _drafts
        print("读取文章列表成功")
        return posts

    def get_pages(self):
        posts = self.repo.get_contents(self.path + 'source', ref=self.branch)
        results = list()
        for post in posts:
            if post.type == "dir":
                for i in self.repo.get_contents(
                        self.path + post.path,
                        ref=self.branch):
                    if i.type == "file":
                        if i.name == "index.md" or i.name == "index.html":
                            results.append({"name": post.name, "path": i.path, "size": i.size})
                            break
        print("读取页面列表成功")
        return results

    def get_configs(self):
        results = list()
        # # 检索 .github/workflows 仅最多一层目录
        # try:
        #     sources = self.repo.get_contents(self.path + ".github/workflows", ref=self.branch)
        #     for source in sources:
        #         if source.type == "file":
        #             try:
        #                 if source.name[-4:] in [".yml", "yaml"]:
        #                     results.append(
        #                         {"name": source.name, "path": source.path, "size": source.size})
        #             except:
        #                 pass
        #         if source.type == "dir":
        #             for post in self.repo.get_contents(source.path, ref=self.branch):
        #                 try:
        #                     if post.name[-4:] in ["。yml", "yaml"]:
        #                         results.append(
        #                             {"name": post.name, "path": post.path, "size": post.size})
        #                 except:
        #                     pass
        # except:
        #     pass
        # 检索根目录
        posts = self.repo.get_contents(self.path, ref=self.branch)
        for post in posts:
            try:
                if post.name[-4:] in [".yml", "yaml"]:
                    results.append({"name": post.name, "path": post.path, "size": post.size})
            except:
                pass
        # 检索 themes 仅下一级目录下的文件
        try:
            themes = self.repo.get_contents(self.path + "themes", ref=self.branch)
            for theme in themes:
                if theme.type == "dir":
                    for post in self.repo.get_contents(theme.path, ref=self.branch):
                        try:
                            if post.name[-4:] in [".yml", "yaml"]:
                                results.append(
                                    {"name": post.name, "path": post.path, "size": post.size})
                        except:
                            pass
        except:
            pass
        # 检索 source 仅最多一层目录
        sources = self.repo.get_contents(self.path + "source", ref=self.branch)
        for source in sources:
            if source.type == "file":
                try:
                    if source.name[-4:] in [".yml", "yaml"]:
                        results.append(
                            {"name": source.name, "path": source.path, "size": source.size})
                except:
                    pass
            if source.type == "dir":
                for post in self.repo.get_contents(source.path, ref=self.branch):
                    try:
                        if post.name[-4:] in [".yml", "yaml"]:
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    except:
                        pass
        print("读取博客配置列表成功")
        return results

    def save(self, file, content, commitchange="Update by Qexo"):
        try:
            self.repo.update_file(self.path + file, commitchange, content,
                                  self.repo.get_contents(self.path + file, ref=self.branch).sha, branch=self.branch)
        except:
            self.repo.create_file(self.path + file, commitchange, content, branch=self.branch)
        print("保存文件{}成功".format(file))
        return True

    def delete(self, path, commitchange="Delete by Qexo"):
        file = self.repo.get_contents(self.path + path, ref=self.branch)
        if not isinstance(file, list):
            self.repo.delete_file(self.path + path, commitchange, file.sha, branch=self.branch)
        else:
            for i in file:
                self.repo.delete_file(self.path + i.path, commitchange, i.sha, branch=self.branch)
        print("删除文件{}成功".format(path))
        return True

    def delete_hooks(self):
        for hook in self.repo.get_hooks():  # 删除所有HOOK
            hook.delete()
        print("删除所有WebHook成功")
        return True

    def create_hook(self, config):
        self.repo.create_hook(active=True, config=config, events=["push"], name="web")
        print("创建WebHook成功{}".format(config))
        return True
