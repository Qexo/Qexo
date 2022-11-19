from .exceptions import NoSuchProviderError


class Provider(object):
    params = None

    def get_content(self, file):
        ...

    def get_path(self, path):
        ...

    def save(self, file, content):
        ...

    def delete(self, path):
        ...

    def build(self):
        return False

    def delete_hooks(self):
        return False

    def create_hook(self, config):
        return False

    def get_post(self, post):
        try:
            content = self.get_content("source/_drafts/" + post)
            print("从草稿中获取文章{}成功".format(post))
        except:
            content = self.get_content("source/_posts/" + post)
            print("获取文章{}成功".format(post))
        return content

    def get_posts(self, path=""):
        _posts = list()
        _drafts = list()
        names = list()
        try:
            drafts = self.get_path('source/_drafts' + path)["data"]
            for i in range(len(drafts)):
                if drafts[i]["type"] == "file" and drafts[i]["name"][-2:] == "md":
                    _drafts.append({"name": drafts[i]["path"].split("source/_drafts/")[1][0:-3],
                                    "fullname": drafts[i]["path"].split("source/_drafts/")[1],
                                    "path": drafts[i]["path"],
                                    "size": drafts[i]["size"],
                                    "status": False})
                    names.append(drafts[i]["path"].split("source/_drafts/")[1])
                if drafts[i]["type"] == "dir":
                    dir_content = self.get_posts(path=drafts[i]["path"].split("source/_drafts")[1])
                    for file in dir_content:
                        if "source/_drafts" in file["path"]:
                            _drafts.append(file)
                            names.append(file["fullname"])
        except Exception as e:
            print("读取草稿错误: {}，跳过".format(repr(e)))
        try:
            posts = self.get_path('source/_posts' + path)["data"]
            for i in range(len(posts)):
                if posts[i]["type"] == "file" and posts[i]["name"][-2:] == "md":
                    if posts[i]["path"].split("source/_posts/")[1] not in names:
                        _posts.append(
                            {"name": posts[i]["path"].split("source/_posts/")[1][0:-3],
                             "fullname": posts[i]["path"].split("source/_posts/")[1],
                             "path": posts[i]["path"],
                             "size": posts[i]["size"],
                             "status": True})
                if posts[i]["type"] == "dir":
                    dir_content = self.get_posts(path=posts[i]["path"].split("source/_posts")[1])
                    for file in dir_content:
                        if ("source/_posts" in file["path"]) and (file["fullname"] not in names):
                            _posts.append(file)
                            names.append(file["fullname"])
        except Exception as e:
            print("读取文章出错: {}，跳过".format(repr(e)))
        posts = _posts + _drafts
        print("读取文章列表成功")
        return posts

    def get_pages(self):
        posts = self.get_path('source')["data"]
        results = list()
        for post in posts:
            if post["type"] == "dir":
                for i in self.get_path(post["path"])["data"]:
                    if i["type"] == "file":
                        if i["name"] == "index.md" or i["name"] == "index.html":
                            results.append({"name": post["name"], "path": i["path"], "size": i["size"]})
                            break
        print("读取页面列表成功")
        return results

    def get_configs(self):
        results = list()
        posts = self.get_path("")["data"]
        for post in posts:
            try:
                if post["name"][-4:] in [".yml", "yaml"]:
                    results.append({"name": post["name"], "path": post["path"], "size": post["size"]})
            except:
                pass
        # 检索 themes 仅下一级目录下的文件
        try:
            themes = self.get_path("themes")["data"]
            for theme in themes:
                if theme["type"] == "dir":
                    for post in self.get_path(theme["path"])["data"]:
                        try:
                            if post["name"][-4:] in [".yml", "yaml"]:
                                results.append(
                                    {"name": post["name"], "path": post["path"], "size": post["size"]})
                        except:
                            pass
        except:
            pass
        # 检索 source 仅最多一层目录
        sources = self.get_path("source")["data"]
        for source in sources:
            if source["type"] == "file":
                try:
                    if source["name"][-4:] in [".yml", "yaml"]:
                        results.append({"name": source["name"], "path": source["path"], "size": source["size"]})
                except:
                    pass
            if source["type"] == "dir":
                for post in self.get_path(source["path"])["data"]:
                    try:
                        if post["name"][-4:] in [".yml", "yaml"]:
                            results.append({"name": post["name"], "path": post["path"], "size": post["size"]})
                    except:
                        pass
        print("读取博客配置列表成功")
        return results


from .providers import _all_providers


def all_providers():
    return list(_all_providers.keys())


def get_params(provider_name):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name].params


def get_provider(provider_name: str, **kwargs):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name](**kwargs)
