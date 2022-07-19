import os
from core.QexoSettings import ALL_SETTINGS
import requests
from django.template.defaulttags import register
from core.QexoSettings import QEXO_VERSION
from .models import Cache, SettingModel, FriendModel, NotificationModel, CustomModel, StatisticUV, StatisticPV
import github
import json
from urllib.parse import quote
from datetime import timezone, timedelta, date, datetime
from time import time
from hashlib import md5
from urllib3 import disable_warnings
from markdown import markdown
from zlib import crc32 as zlib_crc32
from urllib.parse import quote
from time import strftime, localtime
import tarfile
import html2text as ht
from hexoweb.libs.onepush import notify, get_notifier
from hexoweb.libs.onepush import all_providers as onepush_providers
from hexoweb.libs.platforms import get_provider, all_providers, get_params
from hexoweb.libs.image import get_image_host
from hexoweb.libs.image import get_params as get_image_params
from hexoweb.libs.image import all_providers as all_image_providers
import yaml
import re
import shutil

disable_warnings()


def get_setting(name):
    try:
        return SettingModel.objects.get(name=name).content
    except:
        return ""


def update_provider():
    global _Provider
    _provider = json.loads(get_setting("PROVIDER"))
    _Provider = get_provider(_provider["provider"], **_provider["params"])
    return _Provider


try:
    _Provider = update_provider()
except:
    pass


def Provider():
    try:
        return _Provider
    except:
        return update_provider()


@register.filter  # 在模板中使用range()
def get_range(value):
    return range(1, value + 1)


@register.filter
def div(value, div):  # 保留两位小数的除法
    return round((value / div), 2)


def get_cdn():
    cdn_prev = get_setting("CDN_PREV")
    if not cdn_prev:
        save_setting("CDN_PREV", "https://unpkg.com/")
        cdn_prev = "https://unpkg.com/"
    return cdn_prev


def get_cdnjs():
    cdnjs = get_setting("CDNJS")
    if not cdnjs:
        save_setting("CDNJS", "https://cdn.staticfile.org/")
        cdnjs = "https://cdn.staticfile.org/"
    return cdnjs


def get_post(post):
    return Provider().get_post(post)


# 获取用户自定义的样式配置
def get_custom_config():
    context = {"cdn_prev": get_cdn(), "cdnjs": get_cdnjs()}
    context["QEXO_NAME"] = get_setting("QEXO_NAME")
    if not context["QEXO_NAME"]:
        save_setting('QEXO_NAME', 'Hexo管理面板')
        context["QEXO_NAME"] = get_setting("QEXO_NAME")
    context["QEXO_SPLIT"] = get_setting("QEXO_SPLIT")
    if not context["QEXO_SPLIT"]:
        save_setting('QEXO_SPLIT', ' - ')
        context["QEXO_SPLIT"] = get_setting("QEXO_SPLIT")
    context["QEXO_LOGO"] = get_setting("QEXO_LOGO")
    if not context["QEXO_LOGO"]:
        save_setting('QEXO_LOGO',
                     'https://unpkg.com/qexo-static@1.4.0/assets' +
                     '/img/brand/qexo.png')
        context["QEXO_LOGO"] = get_setting("QEXO_LOGO")
    context["QEXO_ICON"] = get_setting("QEXO_ICON")
    if not context["QEXO_ICON"]:
        save_setting('QEXO_ICON',
                     'https://unpkg.com/qexo-static@1.4.0/assets' +
                     '/img/brand/favicon.ico')
        context["QEXO_ICON"] = get_setting("QEXO_ICON")
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


def update_posts_cache(s=None):
    if s:
        old_cache = Cache.objects.filter(name="posts")
        if old_cache.count():
            posts = json.loads(old_cache.first().content)
            i = 0
            while i < len(posts):
                if s.upper() not in posts[i]["name"].upper():
                    del posts[i]
                    i -= 1
                i += 1
            cache_name = "posts." + str(s)
            update_caches(cache_name, posts)
            return posts
    else:
        old_cache = False
    posts = Provider().get_posts()
    if s:
        if not old_cache.count():
            update_caches("posts", posts)
        i = 0
        while i < len(posts):
            if s.upper() not in posts[i]["name"].upper():
                del posts[i]
                i -= 1
            i += 1
    if s:
        cache_name = "posts." + str(s)
    else:
        cache_name = "posts"
    update_caches(cache_name, posts)
    return posts


def update_pages_cache(s=None):
    if s:
        old_cache = Cache.objects.filter(name="pages")
        if old_cache.count():
            posts = json.loads(old_cache.first().content)
            i = 0
            while i < len(posts):
                if s.upper() not in posts[i]["name"].upper():
                    del posts[i]
                    i -= 1
                i += 1
            cache_name = "pages." + str(s)
            update_caches(cache_name, posts)
            return posts
    results = Provider().get_pages()
    update_caches("pages", results)
    if not s:
        return results
    i = 0
    while i < len(results):
        if s.upper() not in results[i]["name"].upper():
            del results[i]
            i -= 1
        i += 1
    update_caches("pages." + str(s), results)
    return results


def update_configs_cache(s=None):
    if s:
        old_cache = Cache.objects.filter(name="configs")
        if old_cache.count():
            posts = json.loads(old_cache.first().content)
            i = 0
            while i < len(posts):
                if s.upper() not in posts[i]["name"].upper():
                    del posts[i]
                    i -= 1
                i += 1
            cache_name = "configs." + str(s)
            update_caches(cache_name, posts)
            return posts
    results = Provider().get_configs()
    update_caches("configs", results)
    if not s:
        return results
    i = 0
    while i < len(results):
        if s.upper() not in results[i]["name"].upper():
            del results[i]
            i -= 1
        i += 1
    update_caches("configs." + str(s), results)
    return results


def delete_all_caches():
    caches = Cache.objects.all()
    for cache in caches:
        if cache.name != "update":
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


def save_custom(name, content):
    obj = CustomModel.objects.filter(name=name)
    if obj.count() == 1:
        obj.delete()
    if obj.count() > 1:
        for i in obj:
            i.delete()
    new_set = CustomModel()
    new_set.name = str(name)
    if content is not None:
        new_set.content = str(content)
    else:
        new_set.content = ""
    new_set.save()
    return new_set


def save_cache(name, content):
    obj = Cache.objects.filter(name=name)
    if obj.count() == 1:
        obj.delete()
    if obj.count() > 1:
        for i in obj:
            i.delete()
    new_set = Cache()
    new_set.name = str(name)
    if content is not None:
        new_set.content = str(content)
    else:
        new_set.content = ""
    new_set.save()
    return new_set


def get_latest_version():
    context = dict()
    try:
        provider = json.loads(get_setting("PROVIDER"))
        if provider["provider"] == "github":
            user = github.Github(provider["params"]["token"])
            latest = user.get_repo("am-abudu/Qexo").get_latest_release()
            if latest.tag_name and (latest.tag_name != QEXO_VERSION):
                context["hasNew"] = True
            else:
                context["hasNew"] = False
            context["newer"] = latest.tag_name
            context["newer_link"] = latest.html_url
            context["newer_time"] = latest.created_at.astimezone(
                timezone(timedelta(hours=16))).strftime(
                "%Y-%m-%d %H:%M:%S")
            context["newer_text"] = markdown(latest.body).replace("<p>", "<p class=\"text-sm mb-0\">")
            context["status"] = True
        else:
            context["status"] = False
    except:
        context["status"] = False
    return context


def check_if_api_auth(request):
    if request.POST.get("token") == get_setting("WEBHOOK_APIKEY"):
        return True
    if request.GET.get("token") == get_setting("WEBHOOK_APIKEY"):
        return True
    return False


def check_if_vercel():
    return True if os.environ.get("VERCEL") else False


def get_crc16(x, _hex=False):
    x = str(x)
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a)
    return str(int(s[2:4] + s[4:6], 16)) if _hex is False else (s[2:4] + s[4:6])


def get_crc32(x, _hex=False):
    return str(zlib_crc32(x.encode("utf8"))) if _hex is False else hex(
        zlib_crc32(x.encode("utf8")))[2:]


def get_crc_by_time(_strtime, alg, rep):
    if rep == "hex":
        use_hex = True
    else:
        use_hex = False
    if alg != "crc16" and alg != "crc32":
        return ""
    return get_crc16(_strtime.replace(".", "0"), _hex=use_hex) if alg == "crc16" else get_crc32(
        _strtime.replace(".", "0"), _hex=use_hex)


def fix_all(all_settings=ALL_SETTINGS):
    counter = 0
    already = list()
    settings = SettingModel.objects.all()
    for query in settings:
        if query.name not in already:
            already.append(query.name)
        else:
            query.delete()
            counter += 1
    for setting in all_settings:
        if (setting[0] not in already) or (setting[2]):
            save_setting(setting[0], setting[1])
            counter += 1
    return counter


def get_project_detail():
    return {"token": get_setting("VERCEL_TOKEN"),
            "id": get_setting("PROJECT_ID")}


def checkBuilding(projectId, token):
    r = 0
    url = "https://api.vercel.com/v6/deployments/?projectId=" + projectId
    header = dict()
    header["Authorization"] = "Bearer " + token
    header["Content-Type"] = "application/json"
    response = requests.get(url, headers=header).json()
    result = response["deployments"]
    for deployment in result:
        if deployment['state'] == "BUILDING" or deployment['state'] == "INITIALIZING":
            r += 1
    return r


def file_get_contents(file):
    with open(file, 'r', encoding="utf8") as f:
        content = f.read()
    return content


def getEachFiles(base, path=""):
    file = list()
    handler = os.listdir(base + "/" + path)
    for item in handler:
        if item != '.git':
            fromfile = base + "/" + path + "/" + item
            if os.path.isdir(fromfile):
                file += getEachFiles(base, path + "/" + item)
            else:
                file.append({"file": path + "/" + item,
                             "data": file_get_contents(fromfile)})
    return file


def getIndexFile(base, path=""):
    index = ""
    handler = os.listdir(base + "/" + path)
    for item in handler:
        if item != 'manage.py':
            fromfile = base + "/" + path + "/" + item
            if os.path.isdir(fromfile):
                tmp = getIndexFile(base, path + "/" + item)
                if tmp:
                    index = tmp
        else:
            index = path
            break
    return index


def VercelUpdate(appId, token, sourcePath=""):
    if checkBuilding(appId, token):
        return {"status": False, "msg": "Another building is in progress."}
    url = "https://api.vercel.com/v13/deployments"
    header = dict()
    data = dict()
    header["Authorization"] = "Bearer " + token
    header["Content-Type"] = "application/json"
    data["name"] = "qexo"
    data["project"] = appId
    data["target"] = "production"
    if sourcePath == "":
        sourcePath = os.path.abspath("")
    data["files"] = getEachFiles(sourcePath)
    response = requests.post(url, data=json.dumps(data), headers=header)
    return {"status": True, "msg": response.json()}


def VercelOnekeyUpdate(auth='am-abudu', project='Qexo', branch='master'):
    vercel_config = get_project_detail()
    tmpPath = '/tmp'
    # 从github下载对应tar.gz，并解压
    url = 'https://github.com/' + auth + '/' + project + '/tarball/' + quote(branch) + '/'
    # print("download from " + url)
    _tarfile = tmpPath + '/github.tar.gz'
    with open(_tarfile, "wb") as file:
        file.write(requests.get(url).content)
    # print("ext files")
    t = tarfile.open(_tarfile)
    t.extractall(path=tmpPath)
    t.close()
    os.remove(_tarfile)
    outPath = os.path.abspath(tmpPath + getIndexFile(tmpPath))
    # print("outPath: " + outPath)
    if outPath == '':
        return {"status": False, "msg": 'error: no outPath'}
    return VercelUpdate(vercel_config["id"], vercel_config["token"], outPath)


def copy_all_files(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    if os.path.exists(src_dir):
        for file in os.listdir(src_dir):
            file_path = os.path.join(src_dir, file)
            dst_path = os.path.join(dst_dir, file)
            if os.path.isfile(os.path.join(src_dir, file)):
                shutil.copyfile(file_path, dst_path)
            else:
                shutil.copytree(file_path, dst_path)


def LocalOnekeyUpdate(auth='am-abudu', project='Qexo', branch='master'):
    Path = os.path.abspath("")
    tmpPath = os.path.abspath("./_tmp")
    if not os.path.exists(tmpPath):
        os.mkdir(tmpPath)
    _tarfile = tmpPath + '/github.tar.gz'
    try:
        url = 'https://github.com/' + auth + '/' + project + '/tarball/' + quote(branch) + '/'
        with open(_tarfile, "wb") as file:
            file.write(requests.get(url).content)
    except:
        url = 'https://hub.fastgit.xyz/' + auth + '/' + project + '/tarball/' + quote(branch) + '/'
        with open(_tarfile, "wb") as file:
            file.write(requests.get(url).content)
    t = tarfile.open(_tarfile)
    t.extractall(path=tmpPath)
    t.close()
    os.remove(_tarfile)
    outPath = os.path.abspath(tmpPath + getIndexFile(tmpPath))
    filelist = os.listdir(Path)
    for filename in filelist:  # delete all files except tmp
        if not filename in ["_tmp", "configs.py", "db"]:
            if os.path.isfile(filename):
                os.remove(filename)
            elif os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                pass
    copy_all_files(outPath, Path)
    shutil.rmtree(tmpPath)
    return {"status": True, "msg": "更新成功!"}


def CreateNotification(label, content, now):
    N = NotificationModel()
    N.label = label
    N.content = content
    N.time = str(float(now))
    N.save()
    try:
        notify_me(label, content)
    except:
        pass
    return N


def GetNotifications():
    N = NotificationModel.objects.all()
    result = list()
    for notification in N:
        result.append(dict(
            label=notification.label,
            content=notification.content.replace("\n", "<br>"),
            timestamp=notification.time,
            time=strftime("%Y-%m-%d %H:%M:%S", localtime(float(notification.time)))
        ))
    return result


def DelNotification(_time):
    N = NotificationModel.objects.get(time=_time)
    N.delete()
    return N


def notify_me(title, content):
    config = get_setting("ONEPUSH")
    if config:
        config = json.loads(config)
    else:
        return False
    if config.get("markdown") == "true":
        text_maker = ht.HTML2Text()
        text_maker.bypass_tables = False
        content = text_maker.handle(content)
    ntfy = notify(config["notifier"], **config["params"], title="Qexo消息: " + title, content=content)
    try:
        return ntfy.text
    except:
        return "OK"


def get_domain(domain):
    return domain.split("/")[2].split(":")[0] if domain[:4] == "http" else domain.split(":")[0]


def verify_provider(provider):
    try:
        provider = get_provider(provider["provider"], **provider["params"])
        home = provider.get_path("")
        hexo = 0
        indexhtml = 0
        source = 0
        pack = 0
        theme = 0
        theme_dir = 0
        config_hexo = 0
        config_theme = 0
        status = 0
        # 校验根目录文件
        for file in home["data"]:
            if file["name"] == "index.html" and file["type"] == "file":
                indexhtml = 1
            if file["name"] == "source" and file["type"] == "dir":
                source = 1
            if file["name"] == "themes" and file["type"] == "dir":
                theme_dir = 1
            if file["name"] == "package.json" and file["type"] == "file":
                pack = "package.json"
            if file["name"] == "_config.yml" and file["type"] == "file":
                config_hexo = "_config.yml"
        # 读取主题 校验主题配置
        try:
            if config_hexo:
                res = provider.get_content("_config.yml")
                content = yaml.load(res, Loader=yaml.SafeLoader)
                if content.get("theme"):
                    theme = content.get("theme")
                    for file in home["data"]:
                        if file["name"] == "_config.{}.yml".format(theme) and file["type"] == "file":
                            config_theme = "_config.{}.yml".format(theme)
                            break
                    if (not config_theme) and theme_dir:
                        theme_path = provider.get_path("themes/" + theme)
                        for file in theme_path["data"]:
                            if file["name"] == "_config.yml" and file["type"] == "file":
                                config_theme = "themes/" + theme + "_config.yml"
                                break
        except:
            pass
        # 校验 Package.json 及 Hexo
        if pack:
            try:
                content = json.loads(provider.get_content("package.json"))
                if content:
                    if content.get("hexo"):
                        if content["hexo"].get("version"):
                            hexo = content["hexo"].get("version")
                    if content.get("dependencies"):
                        if content["dependencies"].get("hexo"):
                            hexo = content["dependencies"].get("hexo")
            except:
                pass
        # 总结校验
        if hexo and config_hexo and (not indexhtml) and source and theme and pack and config_theme:
            status = 1
        return {
            "status": status,
            "hexo": hexo,
            "config_theme": config_theme,
            "config_hexo": config_hexo,
            "indexhtml": indexhtml,
            "source": source,
            "theme": theme,
            "theme_dir": theme_dir,
            "package": pack,
        }
    except:
        return {"status": -1}


def get_post_details(article):
    front_matter = yaml.safe_load(
        re.search(r"---([\s\S]*?)---", article, flags=0).group()[3:-4].replace("{{ date }}",
                                                                               strftime("%Y-%m-%d %H:%M:%S", localtime(time()))).replace(
            "{{ abbrlink }}", get_crc_by_time(str(time()), get_setting("ABBRLINK_ALG"), get_setting("ABBRLINK_REP"))).replace("{",
                                                                                                                              "").replace(
            "}", "")) if article[:3] == "---" else json.loads(
        "{{{}}}".format(re.search(r";;;([\s\S]*?);;;", article, flags=0).group()[3:-4].replace("{{ date }}",
                                                                                               strftime("%Y-%m-%d %H:%M:%S",
                                                                                                        localtime(time()))).replace(
            "{{ abbrlink }}", get_crc_by_time(str(time()), get_setting("ABBRLINK_ALG"), get_setting("ABBRLINK_REP")))))
    for key in front_matter.keys():
        if type(front_matter.get(key)) == datetime:
            front_matter[key] = front_matter[key].strftime("%Y-%m-%d %H:%M:%S")
    passage = repr(re.search(r"[;-][;-][;-]([\s\S]*)", article[3:], flags=0).group()[3:]).replace("<", "\\<").replace(">", "\\>").replace(
        "!", "\\!")
    return front_matter, passage
