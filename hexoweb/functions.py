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
from hexoweb.libs.platforms import get_provider

disable_warnings()

Provider = json.loads(SettingModel.objects.get(name="PROVIDER").content)
Provider = get_provider(Provider["provider"], **Provider["params"])


@register.filter  # 在模板中使用range()
def get_range(value):
    return range(1, value + 1)


@register.filter
def div(value, div):  # 保留两位小数的除法
    return round((value / div), 2)


def get_cdn():
    try:
        cdn_prev = SettingModel.objects.get(name="CDN_PREV").content

    except:
        save_setting("CDN_PREV", "https://unpkg.com/")
        cdn_prev = "https://unpkg.com/"
    return cdn_prev


def get_cdnjs():
    try:
        cdnjs = SettingModel.objects.get(name="CDNJS").content

    except:
        save_setting("CDNJS", "https://cdnjs.cloudflare.com/ajax/libs/")
        cdnjs = "https://cdnjs.cloudflare.com/ajax/libs/"
    return cdnjs


def get_post(post):
    return Provider.get_post(post)

def get_setting(name):
    try:
        return SettingModel.objects.get(name=name).content
    except:
        return ""


# 获取用户自定义的样式配置
def get_custom_config():
    context = {"cdn_prev": get_cdn(), "cdnjs": get_cdnjs()}
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
    posts = Provider.get_posts()
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
    results = Provider.get_pages()
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
    results = Provider.get_configs()
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
