from .functions import *
from django.views.decorators.csrf import csrf_exempt
import random
from .models import ImageModel
from django.shortcuts import render
from time import strftime, localtime
from time import time
from django.http.response import HttpResponseForbidden


# 保存内容 pub/save
@csrf_exempt
def save(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = request.POST.get('file')
        content = request.POST.get('content')
        try:
            repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
            branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
            repo.update_file(repo_path + file_path, "Update by QexoPubAPI", content,
                             repo.get_contents(repo_path + file_path, ref=branch).sha,
                             branch=branch)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 保存文章 pub/save_post
@csrf_exempt
def save_post(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_name = request.POST.get('file')
        content = request.POST.get('content')
        try:
            repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
            branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
            # 删除草稿
            try:
                repo.delete_file(repo_path + "source/_drafts/" + file_name, "Delete by QexoPubAPI",
                                 repo.get_contents(repo_path + "source/_drafts/" + file_name,
                                                   ref=branch).sha,
                                 branch=branch)
            except:
                pass
            # 创建/更新文章
            try:
                repo.update_file(repo_path + "source/_posts/" + file_name, "Update by QexoPubAPI",
                                 content,
                                 repo.get_contents(repo_path + "source/_posts/" + file_name,
                                                   ref=branch).sha, branch=branch)
            except:
                repo.create_file(repo_path + "source/_posts/" + file_name, "Update by QexoPubAPI",
                                 content, branch=branch)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 保存草稿 pub/save_draft
@csrf_exempt
def save_draft(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_name = request.POST.get('file')
        content = request.POST.get('content')
        try:
            repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
            branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
            # 创建/更新草稿
            try:
                repo.update_file(repo_path + "source/_drafts/" + file_name, "Update by QexoPubAPI",
                                 content,
                                 repo.get_contents(repo_path + "source/_drafts/" + file_name,
                                                   ref=branch).sha, branch=branch)
            except:
                repo.create_file(repo_path + "source/_drafts/" + file_name, "Update by QexoPubAPI",
                                 content, branch=branch)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 新建内容 pub/new
@csrf_exempt
def new(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = request.POST.get('file')
        content = request.POST.get('content')
        try:
            repo.create_file(path=SettingModel.objects.get(name="GH_REPO_PATH").content + file_path,
                             message="Create by QexoPubAPI", content=content,
                             branch=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 删除内容 pub/delete
@csrf_exempt
def delete(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
        repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
        file_path = request.POST.get('file')
        try:
            file = repo.get_contents(file_path, ref=branch)
            if not isinstance(file, list):
                repo.delete_file(repo_path + file_path, "Delete by QexoPubAPI", file.sha, branch=branch)

            else:
                for i in file:
                    repo.delete_file(repo_path + i.path, "Delete by QexoPubAPI", i.sha, branch=branch)
            context = {"msg": "OK!", "status": True}
            # Delete Caches
            if ("_posts" in file_path) or ("_drafts" in file_path):
                delete_posts_caches()
            else:
                delete_all_caches()
        except Exception as error:
            context = {"msg": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 删除文章 pub/delete_post
@csrf_exempt
def delete_post(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
        repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
        filename = request.POST.get('file')
        try:
            try:
                repo.delete_file(repo_path + "source/_posts/" + filename, "Delete by QexoPubAPI",
                                 repo.get_contents(
                                     repo_path + "source/_posts/" + filename, ref=branch).sha,
                                 branch=branch)
            except:
                pass
            try:
                repo.delete_file(repo_path + "source/_drafts/" + filename, "Delete by QexoPubAPI",
                                 repo.get_contents(
                                     repo_path + "source/_drafts/" + filename, ref=branch).sha,
                                 branch=branch)
            except:
                pass
            delete_posts_caches()
            context = {"msg": "删除成功！", "status": True}
        except Exception as error:
            context = {"msg": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 自动设置 Webhook 事件 pub/create_webhook
@csrf_exempt
def create_webhook_config(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        try:
            if SettingModel.objects.filter(name="WEBHOOK_APIKEY"):
                config = {
                    "content_type": "json",
                    "url": request.POST.get("uri") + "?token=" + SettingModel.objects.get(
                        name="WEBHOOK_APIKEY").content
                }
            else:
                save_setting("WEBHOOK_APIKEY", ''.join(
                    random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12)))
                config = {
                    "content_type": "json",
                    "url": request.POST.get("uri") + "?token=" + SettingModel.objects.get(
                        name="WEBHOOK_APIKEY").content
                }
            repo = get_repo()
            for hook in repo.get_hooks():  # 删除所有HOOK
                hook.delete()
            repo.create_hook(active=True, config=config, events=["push"], name="web")
            context = {"msg": "设置成功！", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有文章 pub/get_posts
@csrf_exempt
def get_posts(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        cache = Cache.objects.filter(name="posts")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_posts_cache()
        context = {"status": True, "posts": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有页面 pub/get_pages
@csrf_exempt
def get_pages(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        cache = Cache.objects.filter(name="pages")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_pages_cache()
        context = {"status": True, "pages": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有配置 pub/get_configs
@csrf_exempt
def get_configs(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        cache = Cache.objects.filter(name="configs")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_configs_cache()
        context = {"status": True, "configs": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有图片 pub/get_images
@csrf_exempt
def get_images(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        posts = list()
        images = ImageModel.objects.all()
        for i in images:
            posts.append({"name": i.name, "size": int(i.size), "url": i.url,
                          "date": strftime("%Y-%m-%d %H:%M:%S",
                                           localtime(float(i.date))),
                          "time": i.date})
        context = {"status": True, "images": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 自动修复程序 api/fix
@csrf_exempt
def auto_fix(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        counter = fix_all()
        msg = "尝试自动修复了 {} 个字段，请在稍后检查和修改配置".format(counter)
        context = {"msg": msg, "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取友情链接 pub/friends
@csrf_exempt
def friends(request):
    try:
        friends = FriendModel.objects.all()
        data = list()
        for i in friends:
            if i.status:
                data.append({"name": i.name, "url": i.url, "image": i.imageUrl,
                             "description": i.description,
                             "time": i.time})
        context = {"data": data, "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 新增友链 pub/add_friend
@csrf_exempt
def add_friend(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        friend = FriendModel()
        friend.name = request.POST.get("name")
        friend.url = request.POST.get("url")
        friend.imageUrl = request.POST.get("image")
        friend.description = request.POST.get("description")
        friend.time = str(float(time()))
        friend.status = request.POST.get("status") == "显示"
        friend.save()
        context = {"msg": "添加成功！", "time": friend.time, "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 编辑友链 pub/edit_friend
@csrf_exempt
def edit_friend(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.name = request.POST.get("name")
        friend.url = request.POST.get("url")
        friend.imageUrl = request.POST.get("image")
        friend.description = request.POST.get("description")
        friend.status = request.POST.get("status") == "显示"
        friend.save()
        context = {"msg": "修改成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 删除友链 pub/del_friend
@csrf_exempt
def del_friend(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 申请友链 pub/ask_friend
@csrf_exempt
def ask_friend(request):
    try:
        if SettingModel.objects.get(name="ALLOW_FRIEND").content != "是":
            return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                             "status": False})})
        friend = FriendModel()
        friend.name = request.POST.get("name")
        friend.url = request.POST.get("url")
        friend.imageUrl = request.POST.get("image")
        friend.description = request.POST.get("description")
        friend.time = str(float(time()))
        friend.status = False
        friend.save()
        CreateNotification("友链申请 " + friend.name,
                           "站点名: {}\n链接: {}\n图片: {}\n简介: {}\n".format(friend.name, friend.url, friend.imageUrl, friend.description), time())
        context = {"msg": "申请成功！", "time": friend.time, "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取自定义字段 pub/get_custom 无需鉴权
@csrf_exempt
def get_custom(request):
    try:
        context = {
            "data": CustomModel.objects.get(name=request.GET.get("key") if request.GET.get("key") else request.POST.get("key")).content,
            "status": True
        }
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取全部消息 pub/get_notifications
def get_notifications(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！", "status": False})})
    try:
        context = {"data": GetNotifications(), "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取博客基本信息 pub/status
def status(request):
    try:
        cache = Cache.objects.filter(name="posts")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_posts_cache()
        posts_count = len(posts)
        last = SettingModel.objects.get(name="LAST_LOGIN").content
        context = {"data": {"posts": str(posts_count), "last": last}, "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 统计API pub/statistic
def statistic(request):
    try:
        url = str(request.META.get('HTTP_REFERER'))
        allow_domains = SettingModel.objects.get(name="STATISTIC_DOMAINS").content.split(",")
        t, allow = get_domain(url), False
        for allow_domain in allow_domains:
            if allow_domain in t:
                allow = True
                break
        if not (allow and (t and SettingModel.objects.get(name="STATISTIC_ALLOW").content == "是")):
            print("Not allowed domain: " + url)
            return HttpResponseForbidden()
        if url[:7] == "http://":
            url = url[7:]
        elif url[:8] == "https://":
            url = url[8:]
        domain = url.split("/")[0]
        pv = StatisticPV.objects.filter(url=url)
        if pv.count() == 1:
            pv = StatisticPV.objects.get(url=url)
            pv.number += 1
            pv.save()
        else:
            for i in pv:
                i.delete()
            pv = StatisticPV()
            pv.url = url
            pv.number = 1
            pv.save()
        site_pv = StatisticPV.objects.filter(url=domain)
        if site_pv.count() == 1:
            site_pv = site_pv.first()
            site_pv.number += 1
            site_pv.save()
        else:
            for i in site_pv:
                i.delete()
            site_pv = StatisticPV()
            site_pv.url = domain
            site_pv.number = 1
            site_pv.save()
        ip = request.META['HTTP_X_FORWARDED_FOR'] if 'HTTP_X_FORWARDED_FOR' in request.META.keys() else request.META['REMOTE_ADDR']
        uv = StatisticUV.objects.filter(ip=ip)
        if uv.count() >= 1:
            data = json.dumps(
                {"site_pv": site_pv.number, "page_pv": pv.number, "site_uv": StatisticUV.objects.all().count(), "status": True})
            return render(request, 'layouts/json.html', {"data": data})
        uv = StatisticUV()
        uv.ip = ip
        uv.save()
        print("Register uv: " + ip)
        data = json.dumps(
            {"site_pv": site_pv.number, "page_pv": pv.number, "site_uv": StatisticUV.objects.all().count(), "status": True})
        return render(request, 'layouts/json.html', {"data": data})
    except Exception as e:
        print(repr(e))
        return render(request, 'layouts/json.html', {"data": json.dumps({"status": False, "error": repr(e)})})
