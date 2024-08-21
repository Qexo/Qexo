import random
import uuid
import sys

from io import StringIO
from django.http.response import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .functions import *
from .models import ImageModel


# 保存内容 pub/save
@csrf_exempt
def save(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = request.POST.get('file')
        content = request.POST.get('content')
        try:
            Provider().save(file_path, content)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存文章 pub/save_post
@csrf_exempt
def save_post(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_name = request.POST.get('file')
        content = request.POST.get('content')
        front_matter = json.loads(request.POST.get('front_matter'))
        excerpt = ""
        try:
            if get_setting("EXCERPT_POST") == "是":
                excerpt = excerpt_post(content, get_setting("EXCERPT_LENGTH"))
                logging.info(f"截取文章{file_name}摘要: " + excerpt)
                front_matter["excerpt"] = excerpt
            front_matter = "---\n{}---".format(yaml.dump(front_matter, allow_unicode=True))
            if not content.startswith("\n"):
                front_matter += "\n"
            if Provider().save_post(file_name, front_matter + content, status=True):
                context = {"msg": "保存成功并提交部署！", "status": True}
            else:
                context = {"msg": "保存成功！", "status": True}
            if excerpt:
                context["excerpt"] = excerpt
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存草稿 pub/save_draft
@csrf_exempt
def save_draft(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_name = request.POST.get('file')
        content = request.POST.get('content')
        front_matter = json.loads(request.POST.get('front_matter'))
        excerpt = ""
        try:
            # 创建/更新草稿
            if get_setting("EXCERPT_POST") == "是":
                excerpt = excerpt_post(content, get_setting("EXCERPT_LENGTH"))
                logging.info(f"截取文章{file_name}摘要: " + excerpt)
                front_matter["excerpt"] = excerpt
            front_matter = "---\n{}---\n".format(yaml.dump(front_matter, allow_unicode=True))
            if not content.startswith("\n"):
                front_matter += "\n"
            if Provider().save_post(file_name, front_matter + content, status=False):
                context = {"msg": "保存草稿成功并提交部署！", "status": True}
            else:
                context = {"msg": "保存草稿成功！", "status": True}
            if excerpt:
                context["excerpt"] = excerpt
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除内容 pub/delete
@csrf_exempt
def delete(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = request.POST.get('file')
        try:
            Provider().delete(file_path)
            context = {"msg": "OK!", "status": True}
            # Delete Caches
            delete_all_caches()
        except Exception as error:
            context = {"msg": repr(error)}
    return JsonResponse(safe=False, data=context)


# 自动设置 Webhook 事件 pub/create_webhook
@csrf_exempt
def create_webhook_config(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
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
            Provider().delete_hooks()
            Provider().create_hook(config)
            context = {"msg": "设置成功！", "status": True}
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取所有文章 pub/get_posts
@csrf_exempt
def get_posts(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        cache = Cache.objects.filter(name="posts")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_posts_cache()
        context = {"status": True, "posts": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 获取所有页面 pub/get_pages
@csrf_exempt
def get_pages(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        cache = Cache.objects.filter(name="pages")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_pages_cache()
        context = {"status": True, "pages": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 获取所有配置 pub/get_configs
@csrf_exempt
def get_configs(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        cache = Cache.objects.filter(name="configs")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_configs_cache()
        context = {"status": True, "configs": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 获取所有图片 pub/get_images
@csrf_exempt
def get_images(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
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
    return JsonResponse(safe=False, data=context)


# 自动修复程序 api/fix
@csrf_exempt
def auto_fix(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        counter = fix_all()
        msg = "尝试自动修复了 {} 个字段，请在稍后检查和修改配置".format(counter)
        context = {"msg": msg, "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取友情链接 pub/friends
@csrf_exempt
def friends(request):
    try:
        all_friends = FriendModel.objects.all()
        data = list()
        for i in all_friends:
            if i.status:
                data.append({"name": i.name, "url": i.url, "image": i.imageUrl,
                             "description": i.description,
                             "time": i.time})
        data.sort(key=lambda x: x["time"])
        context = {"data": data, "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 新增友链 pub/add_friend
@csrf_exempt
def add_friend(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
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
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 编辑友链 pub/edit_friend
@csrf_exempt
def edit_friend(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
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
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除友链 pub/del_friend
@csrf_exempt
def del_friend(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 申请友链 pub/ask_friend
@csrf_exempt
def ask_friend(request):
    try:
        if get_setting("ALLOW_FRIEND") != "是":
            return HttpResponseForbidden()
        # 人机验证
        verify = request.POST.get("verify")
        token = get_setting("RECAPTCHA_TOKEN")
        typ = get_setting("FRIEND_RECAPTCHA")
        if typ == "v3":
            if verify:
                captcha = requests.get(
                    "https://recaptcha.google.cn/recaptcha/api/siteverify?secret=" + token + "&response=" + verify).json()
                logging.info("reCaptchaV3结果: " + str(captcha))
                if captcha["score"] <= 0.5:
                    return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
            else:
                logging.info("未收到人机验信息")
                return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
        if typ == "v2":
            if verify:
                captcha = requests.get(
                    "https://recaptcha.google.cn/recaptcha/api/siteverify?secret=" + token + "&response=" + verify).json()
                logging.info("reCaptchaV2结果: " + str(captcha))
                if not captcha["success"]:
                    return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
            else:
                logging.info("未收到人机验信息")
                return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
        # 通过验证
        friend = FriendModel()
        friend.name = request.POST.get("name")
        friend.url = request.POST.get("url")
        friend.imageUrl = request.POST.get("image")
        friend.description = request.POST.get("description")
        friend.time = str(float(time()))
        friend.status = False
        friend.save()
        CreateNotification("友链申请 " + friend.name,
                           "站点名: {}<br>链接: {}<br>图片: {}<br>简介: {}<br>".format(escapeString(friend.name), escapeString(friend.url),
                                                                                       escapeString(friend.imageUrl),
                                                                                       escapeString(friend.description)), time())
        context = {"msg": "申请成功！", "time": friend.time, "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取自定义字段 pub/get_custom 无需鉴权
@csrf_exempt
def get_custom(request):
    try:
        func_str = CustomModel.objects.get(
            name=request.GET.get("key") if request.GET.get("key") else request.POST.get("key")).content
        body = request.GET
        body.update(request.POST)
        body = dict(body)
        # print(body)
        for key in body.keys():
            if len(body[key]) == 1:
                body[key] = body[key][0]
        locals().update(body)
        old_stdout = sys.stdout
        output = sys.stdout = StringIO()
        try:
            print(eval(func_str))
        except Exception:
            try:
                exec(func_str)
            except Exception:
                print(func_str)
        sys.stdout = old_stdout
        context = {
            "data": output.getvalue(),
            "status": True
        }
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 编辑自定义字段 pub/set_custom
@csrf_exempt
def set_custom(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        save_custom(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除自定义的字段 pub/del_custom
@csrf_exempt
def del_custom(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        CustomModel.objects.filter(name=request.POST.get("name")).delete()
        context = {"msg": "删除成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 新建自定义的字段 pub/new_custom
@csrf_exempt
def new_custom(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        save_custom(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取全部消息 pub/get_notifications
@csrf_exempt
def get_notifications(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        context = {"data": GetNotifications(), "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取博客基本信息 pub/status
@csrf_exempt
def status(request):
    try:
        cache = Cache.objects.filter(name="posts")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_posts_cache()
        posts_count = len(posts)
        last = get_setting("LAST_LOGIN")
        context = {"data": {"posts": str(posts_count), "last": last}, "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 统计API pub/statistic
@csrf_exempt
def statistic(request):
    try:
        url = str(request.META.get('HTTP_REFERER'))
        allow_domains = get_setting("STATISTIC_DOMAINS").split(",")
        t, allow = get_domain(url), False
        for allow_domain in allow_domains:
            if allow_domain in t:
                allow = True
                break
        if not (allow and (t and get_setting("STATISTIC_ALLOW") == "是")):
            logging.error("域名未验证: " + url)
            return HttpResponseForbidden()
        domain, url = get_domain_and_path(url)
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
        logging.info("登记页面PV: {} => {}".format(url, pv.number))
        ip = request.META['HTTP_X_FORWARDED_FOR'] if 'HTTP_X_FORWARDED_FOR' in request.META.keys() else request.META[
            'REMOTE_ADDR']
        uv = StatisticUV.objects.filter(ip=ip)
        if uv.count() >= 1:
            return JsonResponse(safe=False,
                                data={"site_pv": site_pv.number, "page_pv": pv.number, "site_uv": StatisticUV.objects.all().count(),
                                      "status": True})
        uv = StatisticUV()
        uv.ip = ip
        uv.save()
        logging.info("登记用户UV: " + ip)
        return JsonResponse(safe=False, data={"site_pv": site_pv.number, "page_pv": pv.number, "site_uv": StatisticUV.objects.all().count(),
                                              "status": True})
    except Exception as e:
        logging.error(repr(e))
        return JsonResponse(safe=False, data={"status": False, "error": repr(e)})


# Waline Webhook通知 pub/waline
@csrf_exempt
def waline(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        data = json.loads(request.body.decode())
        if data.get("type") == "new_comment":
            comment = data["data"]["comment"]
            msg = "评论者: {}\n邮箱: {}\n".format(comment["nick"], comment["mail"])
            if comment.get("link"):
                msg += "网址: {}\n".format(comment["link"])
            msg += "内容: {}\nIP: {}\n时间: {}\n地址: {}\n状态: {}\nUA: {}".format(comment["comment"], comment["ip"], comment["insertedAt"],
                                                                                   comment["url"], comment["status"], comment["ua"])
            CreateNotification("Waline评论通知", msg, time())
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 自定义通知api pub/notifications
@csrf_exempt
def notifications(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        data = json.loads(request.body.decode())
        content = data.get('content')
        title = data.get('title')
        CreateNotification(title, content, time())
        return JsonResponse(safe=False, data={"msg": "添加成功！", "status": True})
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
        return JsonResponse(safe=False, data=context)


# 获取说说 pub/talks
@csrf_exempt
def get_talks(request):
    try:
        page = int(request.GET.get('page')) if request.GET.get('page') else 1
        limit = int(request.GET.get('limit')) if request.GET.get('limit') else 5
        ip = request.META['HTTP_X_FORWARDED_FOR'] if 'HTTP_X_FORWARDED_FOR' in request.META.keys() else request.META[
            'REMOTE_ADDR']  # 使用用户IP判断点赞是否成立
        if not page:
            page = 1
        if not limit:
            limit = 10
        all_talks = TalkModel.objects.all()
        count = all_talks.count()
        all_talks = all_talks.order_by("time")[::-1][(page - 1) * limit:page * limit]
        talks = []
        for i in all_talks:
            t = json.loads(i.like)
            try:
                values = json.loads(i.values)
            except Exception:
                i.values = "{}"
                values = {}
                i.save()
            talks.append({"id": i.id.hex, "content": i.content, "time": i.time, "tags": json.loads(i.tags), "like": len(t) if t else 0,
                          "liked": True if ip in t else False, "values": values})
        context = {"msg": "获取成功！", "status": True, "count": count, "data": talks}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 点赞说说 pub/like_talk
@csrf_exempt
def like_talk(request):
    try:
        talk_id = request.POST.get('id')
        ip = request.META['HTTP_X_FORWARDED_FOR'] if 'HTTP_X_FORWARDED_FOR' in request.META.keys() else request.META[
            'REMOTE_ADDR']  # 使用用户IP判断点赞是否成立
        talk = TalkModel.objects.get(id=uuid.UUID(hex=talk_id))
        t = json.loads(talk.like)
        if ip in t:
            t.remove(ip)
            talk.like = json.dumps(t)
            talk.save()
            logging.info(ip + "取消点赞: " + talk_id)
            context = {"msg": "取消成功！", "action": False, "status": True}
        else:
            t.append(ip)
            talk.like = json.dumps(t)
            talk.save()
            logging.info(ip + "成功点赞: " + talk_id)
            context = {"msg": "点赞成功！", "action": True, "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存说说 pub/save_talk
@csrf_exempt
def save_talk(request):
    try:
        if not check_if_api_auth(request):
            return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
        context = {"msg": "发布成功!", "status": True}
        if request.POST.get("id"):
            talk = TalkModel.objects.get(id=uuid.UUID(hex=request.POST.get("id")))
            talk.content = request.POST.get("content")
            talk.tags = request.POST.get("tags")
            talk.time = request.POST.get("time")
            talk.values = request.POST.get("values")
            talk.save()
            context["msg"] = "修改成功"
        else:
            talk = TalkModel(content=request.POST.get("content"),
                             tags=request.POST.get("tags"),
                             time=str(int(time())),
                             like="[]",
                             values=request.POST.get("values"))
            talk.save()
            context["id"] = talk.id.hex
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除说说 pub/del_talk
@csrf_exempt
def del_talk(request):
    try:
        if not check_if_api_auth(request):
            return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
        TalkModel.objects.get(id=uuid.UUID(hex=request.POST.get("id"))).delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)
