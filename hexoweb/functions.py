import os
from core.QexoSettings import ALL_SETTINGS
import requests
from django.template.defaulttags import register
from core.QexoSettings import QEXO_VERSION
from .models import Cache, SettingModel, FriendModel, NotificationModel, CustomModel, StatisticUV, StatisticPV
import github
import json
import boto3
from datetime import timezone, timedelta, date
from time import time
from hashlib import md5
from urllib3 import disable_warnings
from markdown import markdown
from zlib import crc32 as zlib_crc32
from urllib.parse import quote
from time import strftime, localtime
import tarfile
from ftplib import FTP
from hexoweb.libs.onepush import notify
import html2text as ht

disable_warnings()


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


def get_cdn():
    try:
        cdn_prev = SettingModel.objects.get(name="CDN_PREV").content
    except:
        save_setting("CDN_PREV", "https://unpkg.com/")
        cdn_prev = "https://unpkg.com/"
    return cdn_prev


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
    context = {"cdn_prev": get_cdn()}
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
                     'https://unpkg.com/qexo-static@1.4.0/assets' +
                     '/img/brand/qexo.png')
        context["QEXO_LOGO"] = SettingModel.objects.get(name="QEXO_LOGO").content
    try:
        context["QEXO_ICON"] = SettingModel.objects.get(name="QEXO_ICON").content
    except:
        save_setting('QEXO_ICON',
                     'https://unpkg.com/qexo-static@1.4.0/assets' +
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
                if s.upper() not in posts[i]["name"].upper():
                    del posts[i]
                    i -= 1
                i += 1
            cache_name = "posts." + str(s)
            update_caches(cache_name, posts)
            return posts
    else:
        old_cache = False
    _posts = list()
    _drafts = list()
    names = list()
    try:
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
            if s.upper() not in posts[i]["name"].upper():
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
                    if i.name == "index.md" or i.name == "index.html":
                        results.append({"name": post.name, "path": i.path, "size": i.size})
                        break
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
    repo = get_repo()
    posts = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content,
                              ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    results = list()
    # 检索 .github/workflows 仅最多一层目录
    try:
        sources = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content +
                                    ".github/workflows",
                                    ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
        for source in sources:
            if source.type == "file":
                try:
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
                        if post.name[-3:] == "yml":
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    except:
                        pass
    except:
        pass
    # 检索根目录
    for post in posts:
        try:
            if post.name[-3:] == "yml":
                results.append({"name": post.name, "path": post.path, "size": post.size})
        except:
            pass
    # 检索 themes 仅下一级目录下的文件
    try:
        themes = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content + "themes",
                                   ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
        for theme in themes:
            if theme.type == "dir":
                for post in repo.get_contents(theme.path,
                                              ref=SettingModel.objects.get(
                                                  name="GH_REPO_BRANCH").content):
                    try:
                        if post.name[-3:] == "yml":
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    except:
                        pass
    except:
        pass
    # 检索 source 仅最多一层目录
    sources = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content +
                                "source",
                                ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    for source in sources:
        if source.type == "file":
            try:
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
                    if post.name[-3:] == "yml":
                        results.append(
                            {"name": post.name, "path": post.path, "size": post.size})
                except:
                    pass

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


def upload_to_s3(file, key_id, access_key, endpoint_url, bucket, path, prev_url):
    # 处理 path
    now = date.today()
    photo_stream = file.read()
    path = path.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}",
                                                                                            str(now.day)) \
        .replace("{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{time}", str(time())) \
        .replace("{extName}", file.name.split(".")[-1]).replace("{md5}",
                                                                md5(photo_stream).hexdigest())

    s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=key_id,
        aws_secret_access_key=access_key,
        endpoint_url=endpoint_url,
        verify=False,
    )
    bucket = s3.Bucket(bucket)
    bucket.put_object(Key=path, Body=photo_stream, ContentType=file.content_type)

    return prev_url + "/" + path


def upload_to_custom(file, api, post_params, json_path, custom_body, custom_header, custom_url):
    if custom_header:
        if custom_body:
            response = requests.post(api, data=json.loads(custom_body),
                                     headers=json.loads(custom_header),
                                     files={post_params: [file.name, file.read(),
                                                          file.content_type]})
        else:
            response = requests.post(api, data={}, headers=json.loads(custom_header),
                                     files={post_params: [file.name, file.read(),
                                                          file.content_type]})
    else:
        if custom_body:
            response = requests.post(api, data=json.loads(custom_body),
                                     files={post_params: [file.name, file.read(),
                                                          file.content_type]})
        else:
            response = requests.post(api, data={},
                                     files={post_params: [file.name, file.read(),
                                                          file.content_type]})
    if json_path:
        json_path = json_path.split(".")
        response.encoding = "utf8"
        data = response.json()
        for path in json_path:
            data = data[path]
    else:
        data = response.text
    return str(custom_url) + data


def upload_to_ftp(file, host, port, user, password, path, prev_url):
    ftp = FTP()
    ftp.set_debuglevel(0)
    ftp.encoding = 'UTF8'
    ftp.connect(host, int(port))
    ftp.login(user, password)
    now = date.today()
    path = path.replace("{year}", str(now.year)).replace("{month}", str(now.month)).replace("{day}",
                                                                                            str(now.day)) \
        .replace("{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{time}", str(time())) \
        .replace("{extName}", file.name.split(".")[-1])
    bufsize = 1024
    ftp.storbinary('STOR ' + path, file, bufsize)
    return prev_url + path


def get_latest_version():
    context = dict()
    try:
        user = github.Github(SettingModel.objects.get(name='GH_TOKEN').content)
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
    except:
        context["status"] = False
    return context


def check_if_api_auth(request):
    if request.POST.get("token") == SettingModel.objects.get(name="WEBHOOK_APIKEY").content:
        return True
    if request.GET.get("token") == SettingModel.objects.get(name="WEBHOOK_APIKEY").content:
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
    return {"token": SettingModel.objects.get(name="VERCEL_TOKEN").content,
            "id": SettingModel.objects.get(name="PROJECT_ID").content}


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


def OnekeyUpdate(auth='am-abudu', project='Qexo', branch='master'):
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


# Twikoo
# Twikoo系列
def TestTwikoo(TwikooDomain, TwikooPassword):
    """
    参数:
        TwikooDomain(Twikoo的接口)--String
        TwikooPassword(Twikoo的管理密码)--String
    返回:
        accessToken(Twikoo的Token) --String
    """
    RequestData = {"event": "LOGIN", "password": md5(TwikooPassword.encode(
        encoding='utf-8')).hexdigest()}
    LoginRequests = requests.post(url=TwikooDomain, json=RequestData)
    accessToken = json.loads(LoginRequests.text)['accessToken']
    return accessToken


def GetComments(url, pass_md5, TwikooDomain):
    """
    参数:
        url(需要获取评论的链接，例如/post/qexo) --String
        TwikooDomain(Twikoo的接口) --String
        pass_md5(Twikoo的密码md5) --String
    返回:
        评论列表:
        [
            {"id":评论id,"nick":昵称,"body":正文,"time":时间(unix时间戳),"hidden":是否隐藏}
        ]
        其中:
        hidden  --Bool
    """
    RequestData = {"event": "COMMENT_GET", "accessToken": pass_md5, "url": url}
    LoginRequests = requests.post(url=TwikooDomain, data=RequestData)
    commentData = json.loads(LoginRequests.text)['data']
    comments = []
    for i in range(len(commentData)):
        id = commentData[i]['id']
        nick = commentData[i]['nick']
        body = commentData[i]['comment']
        time = commentData[i]['created']
        Hidden = commentData[i]['isSpam']
        comments.append({"id": id, "nick": nick, "body": body, "time": time, "hidden": Hidden})
    return comments


def GetAllComments(pass_md5, TwikooDomain, per=0x7FFFFFFF, page=1, key="", type=""):
    """
    参数:
        per(每一页的评论数) --int
        pages(页数)--int
        TwikooDomain(Twikoo的接口)--String
        pass_md5(Twikoo密码的md5)--String
        key(可选，搜索关键字)--String
        type(可选，类型，HIDDEN为被隐藏的评论，VISIBLE为可见评论)
    返回:
        评论列表，格式:
        [
            {"id":评论id,"nick":昵称,"body":正文,"time":时间(unix时间戳),"hidden":是否隐藏}
        ]
        其中:
        hidden  --Bool
    """
    RequestData = {"event": "COMMENT_GET_FOR_ADMIN", "accessToken": pass_md5, "per": per,
                   "page": page, "keyword": key, "type": type}
    LoginRequests = requests.post(url=TwikooDomain, json=RequestData)
    commentData = json.loads(LoginRequests.text)['data']
    comments = []
    for i in range(len(commentData)):
        id = commentData[i]['_id']
        nick = commentData[i]['nick']
        body = commentData[i]['comment']
        time = commentData[i]['created']
        Hidden = commentData[i]['isSpam']
        comments.append({"id": id, "nick": nick, "body": body, "time": time, "hidden": Hidden})
    return comments


def SetComment(pass_md5, TwikooDomain, id, status):
    """
    参数:
        status(是否隐藏) --Bool
        id(评论id)  --String
        TwikooDomain(Twikoo的接口) --String
        pass_md5(Twikoo的密码md5)--String
    返回:
        Succeed或者是Error
    """
    RequestData = {"event": "COMMENT_SET_FOR_ADMIN", "accessToken": pass_md5, "id": id,
                   "set": {"isSpam": status}}
    LoginRequests = requests.post(url=TwikooDomain, json=RequestData)
    code = json.loads(LoginRequests.text)['code']
    if code == 0:
        return 'Succeed'
    else:
        return 'Error'


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
    config = SettingModel.objects.get(name="ONEPUSH").content
    if config:
        config = json.loads(config)
    else:
        return False
    if config.get("markdown") is True:
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
