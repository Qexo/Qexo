from django.template.defaulttags import register
from .models import Cache, SettingModel
import github
import json


@register.filter  # 在模板中使用range()
def get_range(value):
    return range(1, value + 1)


@register.filter
def div(value, div):  # 保留两位小数的除法
    return round((value / div), 2)


def get_repo():
    if SettingModel.objects.filter(name__contains="GH_").count() >= 4:
        repo = github.Github(SettingModel.objects.get(name='GH_TOKEN').content).get_repo(
            SettingModel.objects.get(name="GH_REPO").content)
        return repo
    return False


def get_post(post):
    repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
    branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
    try:
        return get_repo().get_contents(repo_path + "source/_drafts/" + post,
                                       branch).decoded_content.decode("utf8")
    except:
        return get_repo().get_contents(repo_path + "source/_posts/" + post,
                                       branch).decoded_content.decode("utf8")


# 获取用户自定义的样式配置
def get_custom_config():
    context = dict()
    try:
        context["QEXO_NAME"] = SettingModel.objects.get(name="QEXO_NAME").content
    except:
        save_setting('QEXO_NAME', 'Hexo管理面板')
        context["QEXO_NAME"] = SettingModel.objects.get(name="QEXO_NAME").content
    try:
        context["QEXO_SPLIT"] = SettingModel.objects.get(name="QEXO_SPLIT").content
    except:
        save_setting('QEXO_SPLIT', ' - ')
        context["QEXO_SPLIT"] = SettingModel.objects.get(name="QEXO_SPLIT").content
    try:
        context["QEXO_LOGO"] = SettingModel.objects.get(name="QEXO_LOGO").content
    except:
        save_setting('QEXO_LOGO',
                     'https://cdn.jsdelivr.net/gh/am-abudu/Qexo@master/static/assets' +
                     '/img/brand/qexo.png')
        context["QEXO_LOGO"] = SettingModel.objects.get(name="QEXO_LOGO").content
    try:
        context["QEXO_ICON"] = SettingModel.objects.get(name="QEXO_ICON").content
    except:
        save_setting('QEXO_ICON',
                     'https://cdn.jsdelivr.net/gh/am-abudu/Qexo@master/static/assets' +
                     '/img/brand/favicon.ico')
        context["QEXO_ICON"] = SettingModel.objects.get(name="QEXO_ICON").content
    return context


# 更新缓存
def update_caches(name, content, _type="json"):
    caches = Cache.objects.filter(name=name)
    if caches.count():
        caches.delete()
    posts_cache = Cache()
    posts_cache.name = name
    if _type == "json":
        posts_cache.content = json.dumps(content)
    else:
        posts_cache.content = content
    posts_cache.save()


def update_posts_cache(s=None, _path=""):
    repo = get_repo()
    if s:
        old_cache = Cache.objects.filter(name="posts")
        if old_cache.count():
            posts = json.loads(old_cache.first().content)
            i = 0
            while i < len(posts):
                if s not in posts[i]["name"]:
                    del posts[i]
                    i -= 1
                i += 1
            cache_name = "posts." + str(s)
            update_caches(cache_name, posts)
            return posts
    try:
        _posts = list()
        _drafts = list()
        names = list()
        posts = repo.get_contents(
            SettingModel.objects.get(name="GH_REPO_PATH").content + 'source/_posts' + _path,
            ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
        for i in range(len(posts)):
            if posts[i].type == "file":
                _posts.append(
                    {"name": posts[i].path.split("source/_posts/")[1][0:-3],
                     "fullname": posts[i].path.split("source/_posts/")[1],
                     "path": posts[i].path,
                     "size": posts[i].size,
                     "status": True})
                names.append(posts[i].path.split("source/_posts/")[1])
            if posts[i].type == "dir":
                dir_content = update_posts_cache(_path=posts[i].path.split("source/_posts")[1])
                for file in dir_content:
                    if "source/_posts" in file["path"]:
                        _posts.append(file)
                        names.append(file["fullname"])
    except:
        pass
    try:
        drafts = repo.get_contents(
            SettingModel.objects.get(name="GH_REPO_PATH").content + 'source/_drafts' + _path,
            ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
        for i in range(len(drafts)):
            if drafts[i].type == "file":
                if drafts[i].path.split(
                        "source/_drafts/")[1] not in names:
                    _drafts.append({"name": drafts[i].path.split(
                        "source/_drafts/")[1][0:-3], "fullname": drafts[i].path.split(
                        "source/_drafts/")[1],
                                    "path": drafts[i].path,
                                    "size": drafts[i].size, "status": False})
            if drafts[i].type == "dir":
                dir_content = update_posts_cache(_path=drafts[i].path.split("source/_drafts")[1])
                for file in dir_content:
                    if ("source/_drafts" in file["path"]) and (file["fullname"] not in names):
                        _posts.append(file)
                        names.append(file["fullname"])
    except:
        pass
    posts = _posts + _drafts
    if s:
        if not old_cache.count():
            update_caches("posts", posts)
        i = 0
        while i < len(posts):
            if s not in posts[i]["name"]:
                del posts[i]
                i -= 1
            i += 1
    if not _path:
        if s:
            cache_name = "posts." + str(s)
        else:
            cache_name = "posts"
        update_caches(cache_name, posts)
    return posts


def update_pages_cache(s=None):
    repo = get_repo()
    posts = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content + 'source',
                              ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    results = list()
    for post in posts:
        if post.type == "dir":
            for i in repo.get_contents(
                    SettingModel.objects.get(name="GH_REPO_PATH").content + post.path,
                    ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content):
                if i.type == "file":
                    if s:
                        if (i.name == "index.md" or i.name == "index.html") and (
                                str(s) in post.name):
                            results.append({"name": post.name, "path": i.path, "size": i.size})
                            break
                    else:
                        if i.name == "index.md" or i.name == "index.html":
                            results.append({"name": post.name, "path": i.path, "size": i.size})
                            break
    if s:
        cache_name = "pages." + str(s)
    else:
        cache_name = "pages"
    update_caches(cache_name, results)
    return results


def update_configs_cache(s=None):
    repo = get_repo()
    posts = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content,
                              ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    results = list()
    for post in posts:
        try:
            if s:
                if post.name[-3:] == "yml" and s in post.name:
                    results.append({"name": post.name, "path": post.path, "size": post.size})
            else:
                if post.name[-3:] == "yml":
                    results.append({"name": post.name, "path": post.path, "size": post.size})
        except:
            pass

    themes = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content + "themes",
                               ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    for theme in themes:
        if theme.type == "dir":
            for post in repo.get_contents(theme.path,
                                          ref=SettingModel.objects.get(
                                              name="GH_REPO_BRANCH").content):
                try:
                    if s:
                        if post.name[-3:] == "yml" and s in post.name:
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    else:
                        if post.name[-3:] == "yml":
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                except:
                    pass

    sources = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content +
                                "source",
                                ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    for source in sources:
        if source.type == "file":
            try:
                if s:
                    if source.name[-3:] == "yml" and s in source.name:
                        results.append(
                            {"name": source.name, "path": source.path, "size": source.size})
                else:
                    if source.name[-3:] == "yml":
                        results.append(
                            {"name": source.name, "path": source.path, "size": source.size})
            except:
                pass
        if source.type == "dir":
            for post in repo.get_contents(source.path,
                                          ref=SettingModel.objects.get(
                                              name="GH_REPO_BRANCH").content):
                try:
                    if s:
                        if post.name[-3:] == "yml" and s in post.name:
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    else:
                        if post.name[-3:] == "yml":
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                except:
                    pass

    if s:
        cache_name = "configs." + str(s)
    else:
        cache_name = "configs"
    update_caches(cache_name, results)
    return results


def delete_all_caches():
    caches = Cache.objects.all()
    for cache in caches:
        cache.delete()


def delete_posts_caches():
    caches = Cache.objects.all()
    for cache in caches:
        if cache.name[:5] == "posts":
            cache.delete()


def delete_pages_caches():
    caches = Cache.objects.all()
    for cache in caches:
        try:
            name = cache.name[:5]
        except:
            name = ""
        if name == "pages":
            cache.delete()


def save_setting(name, content):
    obj = SettingModel.objects.filter(name=name)
    if obj.count() == 1:
        obj.delete()
    if obj.count() > 1:
        for i in obj:
            i.delete()
    new_set = SettingModel()
    new_set.name = str(name)
    if content is not None:
        new_set.content = str(content)
    else:
        new_set.content = ""
    new_set.save()
    return new_set


def check_if_api_auth(request):
    if request.POST.get("token") == SettingModel.objects.get(name="WEBHOOK_APIKEY").content:
        return True
    if request.GET.get("token") == SettingModel.objects.get(name="WEBHOOK_APIKEY").content:
        return True
    return False
