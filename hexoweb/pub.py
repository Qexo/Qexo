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
        commitchange = request.POST.get('commitchange') if request.POST.get('commitchange') else f"Update {file_path} by Qexo"
        try:
            Provider().save(file_path, content, commitchange)
            context = {"msg": "OK!", "status": True}
            delete_all_caches()
        except Exception as error:
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
        commitchange = request.POST.get('commitchange') if request.POST.get('commitchange') else f"Delete {file_path} by Qexo"
        try:
            if Provider().delete(file_path, commitchange):
                context = {"msg": gettext("DEL_SUCCESS_AND_DEPLOY"), "status": True}
            else:
                context = {"msg": gettext("DEL_SUCCESS"), "status": True}
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
            key = get_setting("WEBHOOK_APIKEY")
            if key:
                url = request.POST.get("uri") + "?token=" + key
            else:
                key = ''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12))
                save_setting("WEBHOOK_APIKEY", key)
                url = request.POST.get("uri") + "?token=" + key
            if Provider().delete_hooks():
                Provider().create_hook(url)
                context = {"msg": gettext("SAVE_SUCCESS"), "status": True}
            else:
                context = {"msg": gettext("PROVIDER_NO_SUPPORT"), "status": False}
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
        search = request.GET.get("s")
        if search:
            cache = Cache.objects.filter(name="posts." + search)
            if cache.count():
                posts = json.loads(cache.first().content)
            else:
                posts = update_posts_cache(search)
        else:
            cache = Cache.objects.filter(name="posts")
            if cache.count():
                posts = json.loads(cache.first().content)
            else:
                posts = update_posts_cache(search)
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
        search = request.GET.get("s")
        if search:
            cache = Cache.objects.filter(name="pages." + search)
            if cache.count():
                posts = json.loads(cache.first().content)
            else:
                posts = update_pages_cache(search)
        else:
            cache = Cache.objects.filter(name="pages")
            if cache.count():
                posts = json.loads(cache.first().content)
            else:
                posts = update_pages_cache(search)
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
        search = request.GET.get("s")
        if search:
            cache = Cache.objects.filter(name="configs." + search)
            if cache.count():
                posts = json.loads(cache.first().content)
            else:
                posts = update_configs_cache(search)
        else:
            cache = Cache.objects.filter(name="configs")
            if cache.count():
                posts = json.loads(cache.first().content)
            else:
                posts = update_configs_cache(search)
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
        search = request.GET.get("s")
        posts = []
        images = ImageModel.objects.all()
        for i in images:
            if not search:
                posts.append({"name": i.name, "size": convert_to_kb_mb_gb(int(i.size)), "url": escape(i.url),
                              "date": strftime("%Y-%m-%d %H:%M:%S",
                                               localtime(float(i.date))),
                              "time": i.date})
            else:
                if search.upper() in i.name.upper() or search.upper() in i.url.upper():
                    posts.append({"name": i.name, "size": convert_to_kb_mb_gb(int(i.size)), "url": escape(i.url),
                                  "date": strftime("%Y-%m-%d %H:%M:%S",
                                                   localtime(float(i.date))),
                                  "time": i.date})
        posts.sort(key=lambda x: x["time"])
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

# 获取全部友情链接 pub/get_friends
@csrf_exempt
def get_friends(request):
    if not check_if_api_auth(request):
        return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
    try:
        search = request.GET.get("s")
        posts = []
        images = FriendModel.objects.all()
        for i in images:
            if not search:
                posts.append(
                    {"name": escapeString(i.name), "url": escapeString(i.url), "image": escapeString(i.imageUrl),
                     "description": escapeString(i.description),
                     "time": i.time,
                     "status": i.status})
            else:
                if search.upper() in i.name.upper() or search.upper() in i.url.upper() or search.upper() in i.description.upper():
                    posts.append(
                        {"name": escapeString(i.name), "url": escapeString(i.url), "image": escapeString(i.imageUrl),
                         "description": escapeString(i.description),
                         "time": i.time,
                         "status": i.status})
        posts.sort(key=lambda x: x["time"])
        context = {"data": posts, "status": True}
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
        referer = request.META.get('HTTP_REFERER', '')
        allow_domains = get_setting("STATISTIC_DOMAINS").split(",")
        domain_name = get_domain(referer)
        if not (domain_name and get_setting("STATISTIC_ALLOW") == "是" and any(d in domain_name for d in allow_domains)):
            logging.error(f"域名未验证: {referer}")
            return HttpResponseForbidden()

        domain, path = get_domain_and_path(referer)
        pv, _ = StatisticPV.objects.get_or_create(url=path, defaults={'number': 0})
        pv.number += 1
        pv.save()

        site_pv, _ = StatisticPV.objects.get_or_create(url=domain, defaults={'number': 0})
        site_pv.number += 1
        site_pv.save()

        logging.info(f"登记页面PV: {path} => {pv.number}")
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', '')
        uv, created = StatisticUV.objects.get_or_create(ip=ip)
        if created:
            logging.info(f"登记用户UV: {ip}")

        total_uv = StatisticUV.objects.count()
        return JsonResponse(safe=False, data={
            "site_pv": site_pv.number,
            "page_pv": pv.number,
            "site_uv": total_uv,
            "status": True
        })
    except Exception as e:
        logging.error(repr(e))
        return JsonResponse(safe=False, data={"status": False, "error": repr(e)})

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

# 获取全部说说 pub/get_all_talks
@csrf_exempt
def get_all_talks(request):
    try:
        if not check_if_api_auth(request):
            return JsonResponse(safe=False, data={"msg": "鉴权错误！", "status": False})
        search = request.GET.get("s")
        posts = []
        talks = TalkModel.objects.all()
        for i in talks:
            t = json.loads(i.like)
            try:
                strtime = strftime("%Y-%m-%d %H:%M:%S", localtime(int(i.time)))
            except Exception:
                strtime = "undefined"
            if not search:
                posts.append({"content": excerpt_post(i.content, 20, mark=False),
                              "tags": ', '.join(json.loads(i.tags)),
                              "time": strtime,
                              "like": len(t) if t else 0,
                              "id": i.id.hex})
            else:
                if search.upper() in i.content.upper() or search in i.tags.upper() or search in i.values.upper():
                    posts.append({"content": excerpt_post(i.content, 20, mark=False),
                                  "tags": ', '.join(json.loads(i.tags)),
                                  "time": strtime,
                                  "like": len(t) if t else 0,
                                  "id": i.id.hex})
        context = {"msg": "获取成功！", "status": True, "data": sorted(posts, key=lambda x: x["time"], reverse=True)}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)