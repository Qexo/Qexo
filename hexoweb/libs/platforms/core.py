from .exceptions import NoSuchProviderError
from .configs import _all_configs as configs
import logging


class Provider(object):
    params = None

    def __init__(self, config):
        self.config = configs[config]

    def get_content(self, file):
        ...

    def get_path(self, path):
        """
        Abstract: should be implemented by subclasses. Return a dict with 'data' key.
        Default returns empty directory.
        """
        return {"data": []}

    def save(self, file, content, commitchange="Update by Qexo", autobuild=True):
        ...

    def delete(self, path, commitchange="Delete by Qexo", autobuild=True):
        ...

    def build(self):
        return False

    def delete_hooks(self):
        return False

    def create_hook(self, config):
        return False

    def get_tree(self, path, depth, exclude=None):  # run if depth >=1
        if not depth:
            return []
        if exclude is None:
            exclude = []
        path = path.replace("\\", "/")
        tree = self.get_path(path)["data"]
        for i in range(len(tree)):
            if tree[i]["name"] in exclude:
                continue
            if tree[i]["type"] == "dir":
                child = self.get_tree(tree[i]["path"], depth - 1, exclude)
                tree += child
        return tree

    def get_posts(self):
        _posts = list()
        _drafts = list()
        names = list()
        for path_index in range(len(self.config["drafts"]["path"])):
            try:
                drafts = self.get_tree(
                    self.config["drafts"]["path"][path_index], self.config["drafts"]["depth"][path_index],
                    self.config["drafts"].get("excludes"))
                for post in drafts:
                    if post["type"] != "file":
                        continue
                    matched_ext = None
                    for ext in self.config["drafts"]["type"]:
                        if post["path"].endswith(ext):
                            matched_ext = ext
                            break
                    if not matched_ext:
                        continue
                    rel_path = post["path"]
                    prefix = self.config["drafts"]["path"][path_index]
                    if prefix:
                        prefix_slash = prefix if prefix.endswith("/") else prefix + "/"
                        name = rel_path[len(prefix_slash):] if rel_path.startswith(prefix_slash) else rel_path
                    else:
                        name = rel_path
                    name = name.rstrip("/")
                    name_no_ext = name[:-len(matched_ext)]
                    _drafts.append({"name": name_no_ext,
                                    "fullname": name_no_ext + matched_ext,
                                    "path": post["path"],
                                    "size": post["size"],
                                    "status": False})
                    names.append(name_no_ext + matched_ext)
            except Exception as e:
                logging.error("读取草稿目录 {} 错误: {}，跳过".format(self.config["drafts"]["path"][path_index], repr(e)))
        for path_index in range(len(self.config["posts"]["path"])):
            try:
                posts = self.get_tree(
                    self.config["posts"]["path"][path_index], self.config["posts"]["depth"][path_index],
                    self.config["posts"].get("excludes"))
                for post in posts:
                    if post["type"] != "file":
                        continue
                    matched_ext = None
                    for ext in self.config["posts"]["type"]:
                        if post["path"].endswith(ext):
                            matched_ext = ext
                            break
                    if not matched_ext:
                        continue
                    rel_path = post["path"]
                    prefix = self.config["posts"]["path"][path_index]
                    if prefix:
                        prefix_slash = prefix if prefix.endswith("/") else prefix + "/"
                        name = rel_path[len(prefix_slash):] if rel_path.startswith(prefix_slash) else rel_path
                    else:
                        name = rel_path
                    name = name.rstrip("/")
                    name_no_ext = name[:-len(matched_ext)]
                    _posts.append({"name": name_no_ext,
                                   "fullname": name_no_ext + matched_ext,
                                   "path": post["path"],
                                   "size": post["size"],
                                   "status": True})
                    names.append(name_no_ext + matched_ext)
            except Exception as e:
                logging.error("读取已发布目录 {} 错误: {}，跳过".format(self.config["posts"]["path"][path_index], repr(e)))
        posts = _posts + _drafts
        logging.info("读取文章列表成功")
        return posts

    def get_pages(self):
        results = list()
        for path_index in range(len(self.config["pages"]["path"])):
            try:
                posts = self.get_tree(
                    self.config["pages"]["path"][path_index], self.config["pages"]["depth"][path_index],
                    self.config["pages"].get("excludes"))
                for post in posts:
                    # only files with configured extensions
                    if post["type"] != "file":
                        continue
                    matched_ext = None
                    for ext in self.config["pages"]["type"]:
                        if post["path"].endswith(ext):
                            matched_ext = ext
                            break
                    if not matched_ext:
                        continue
                    # remove prefix and extension to get display name
                    rel_path = post["path"]
                    prefix = self.config["pages"]["path"][path_index]
                    if prefix:
                        prefix_slash = prefix if prefix.endswith("/") else prefix + "/"
                        if rel_path.startswith(prefix_slash):
                            name = rel_path[len(prefix_slash):]
                        else:
                            name = rel_path
                    else:
                        name = rel_path
                    # strip trailing slash if any
                    if name.endswith("/"):
                        name = name[:-1]
                    # strip extension
                    name = name[:-len(matched_ext)]
                    results.append({"name": name,
                                    "path": post["path"],
                                    "size": post["size"]})
            except Exception as e:
                logging.error("读取页面目录 {} 错误: {}，跳过".format(self.config["pages"]["path"][path_index], repr(e)))
        logging.info("读取页面列表成功")
        return results

    def get_configs(self):
        results = list()
        for path_index in range(len(self.config["configs"]["path"])):
            try:
                posts = self.get_tree(
                    self.config["configs"]["path"][path_index], self.config["configs"]["depth"][path_index],
                    self.config["configs"].get("excludes"))
                for post in posts:
                    if post["type"] != "file":
                        continue
                    matched_ext = None
                    for ext in self.config["configs"]["type"]:
                        if post["path"].endswith(ext):
                            matched_ext = ext
                            break
                    if not matched_ext:
                        continue
                    rel_path = post["path"]
                    prefix = self.config["configs"]["path"][path_index]
                    if prefix:
                        prefix_slash = prefix if prefix.endswith("/") else prefix + "/"
                        name = rel_path[len(prefix_slash):] if rel_path.startswith(prefix_slash) else rel_path
                    else:
                        name = rel_path
                    name = name.rstrip("/")
                    if len(matched_ext) < len(name):
                        name_no_ext = name[:-len(matched_ext)]
                    else:
                        # Skip files where extension is not shorter than the name
                        continue
                    results.append({"name": name_no_ext,
                                    "path": post["path"],
                                    "size": post["size"]})
            except Exception as e:
                logging.error("读取配置 {} 错误: {}，跳过".format(self.config["configs"]["path"][path_index], repr(e)))
        logging.info("读取博客配置列表成功")
        return results

    def get_scaffold(self, scaffold_type):
        return self.get_content(self.config[scaffold_type]["scaffold"])

    def save_post(self, name, content, path=None, status=False, autobuild=True):
        # status: True -> posts, False -> drafts
        # path 若无则保存至默认路径
        if self.config["drafts"]["save_path"]:
            draft_file = self.config["drafts"]["save_path"].replace("${filename}", name)
        else:
            draft_file = None
        save_file = self.config["posts"]["save_path"].replace("${filename}", name)
        if path and (path not in [draft_file, save_file]):
            return [self.save(path, content, f"Save Post {name} by Qexo", autobuild), path, False]
        if status:
            try:
                self.delete(draft_file, f"Delete Post Draft {draft_file} by Qexo", False)
            except:
                logging.info(f"删除草稿{draft_file}失败, 可能无需删除草稿")
            return [self.save(save_file, content, f"Publish Post {save_file} by Qexo", autobuild), save_file, draft_file]
        else:
            if not draft_file:
                raise Exception("当前配置不支持草稿")
            return [self.save(self.config["drafts"]["save_path"].replace("${filename}", name), content,
                              f"Save Post Draft {draft_file} by Qexo", autobuild), draft_file, False]

    def unpublish_post(self, name, path=None, autobuild=True):
        if not self.config["drafts"]["save_path"]:
            raise Exception("当前配置不支持草稿")
        post_file = self.config["posts"]["save_path"].replace("${filename}", name)
        if path and path != post_file:
            draft = self.save_post(name, self.get_content(path), None, False, False)
            self.delete(path, f"Unpublish Post {name} by Qexo", autobuild)
        else:
            draft = self.save_post(name, self.get_content(post_file), None, False, False)
            self.delete(post_file, f"Unpublish Post {name} by Qexo", autobuild)
        return draft

    def publish_post(self, name, path=None, autobuild=True):
        if not self.config["drafts"]["save_path"]:
            raise Exception("当前配置不支持草稿")
        draft_file = self.config["drafts"]["save_path"].replace("${filename}", name)
        if path and path != draft_file:
            draft_file = path
        return self.save_post(name, self.get_content(draft_file), None, True, autobuild)


    def save_page(self, name, content, autobuild=True):
        path = self.config["pages"]["save_path"].replace("${filename}", name)
        return [self.save(path, content, f"Update Page {name} by Qexo", autobuild), path]

    def rename(self, old, new, autobuild=True):
        if old == new:
            return False
        self.save(new, self.get_content(old), f"Rename {old} to {new} by Qexo", False)
        return self.delete(old, f"Rename {old} to {new} by Qexo", autobuild)


from .providers import _all_providers


def all_providers():
    return list(_all_providers.keys())


def all_configs():
    return configs.keys()


def get_params(provider_name):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name].params


def get_provider(provider_name: str, **kwargs):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name](**kwargs)
