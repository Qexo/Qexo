"""
公共API模块 (Public API Module)
提供外部访问的公开接口，用于内容获取、友链管理、说说管理等功能

注意：需要鉴权的接口使用 @api_auth_required 装饰器
     公开接口(friends, status, get_talks, like_talk)无需鉴权
"""
import random
import uuid
import sys
import logging
import unicodedata

from io import StringIO
from django.http.response import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .functions import *
from .models import ImageModel
from .decorators import api_auth_required


# ========================================
# 内容管理类 API (Content Management APIs)
# ========================================

# 保存内容 pub/save
@csrf_exempt
@api_auth_required
def save(request):
    """
    保存文件内容到Provider
    
    POST参数:
        file: 文件路径
        content: 文件内容
        commitchange: 提交信息（可选）
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        content = unicodedata.normalize('NFC', request.POST.get('content'))
        commitchange = request.POST.get('commitchange') if request.POST.get('commitchange') else f"Update {file_path} by Qexo"
        try:
            Provider().save(file_path, content, commitchange)
            context = {"msg": gettext("SAVE_SUCCESS"), "status": True}
            delete_all_caches()
            logging.info(f"保存文件成功: {file_path}")
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除内容 pub/delete
@csrf_exempt
@api_auth_required
def delete(request):
    """
    删除Provider中的文件
    
    POST参数:
        file: 文件路径
        commitchange: 提交信息（可选）
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        commitchange = request.POST.get('commitchange') if request.POST.get('commitchange') else f"Delete {file_path} by Qexo"
        try:
            if Provider().delete(file_path, commitchange):
                context = {"msg": gettext("DEL_SUCCESS_AND_DEPLOY"), "status": True}
            else:
                context = {"msg": gettext("DEL_SUCCESS"), "status": True}
            delete_all_caches()
            logging.info(f"删除文件成功: {file_path}")
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 自动设置 Webhook 事件 pub/create_webhook
@csrf_exempt
@api_auth_required
def create_webhook_config(request):
    """
    自动配置Webhook
    
    POST参数:
        uri: Webhook回调地址
        
    返回:
        {"msg": "消息", "status": True/False, "token": "", "webhook_url": ""}
    """
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        try:
            key = get_setting("WEBHOOK_APIKEY")
            if key:
                context = {"msg": gettext("WEBHOOK_APIKEY_EXISTS"), "status": False}
            else:
                key_plain = ''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12))
                save_setting("WEBHOOK_APIKEY", key_plain)
                url = request.POST.get("uri") + "?token=" + key_plain
                if Provider().delete_hooks():
                    Provider().create_hook(url, "Qexo Hook", ["push"])
                    context = {"msg": gettext("WEBHOOK_CREATE_SUCCESS"), "status": True, "token": key_plain, "webhook_url": url}
                    logging.info(f"Webhook创建成功: {url}")
                else:
                    context = {"msg": gettext("WEBHOOK_NOT_SUPPORT"), "status": False}
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取所有文章 pub/get_posts
@csrf_exempt
@api_auth_required
def get_posts(request):
    """
    获取所有文章列表
    
    GET参数:
        s: 搜索关键词（可选）
        
    返回:
        {"status": True, "posts": [...]}
    """
    try:
        search = request.GET.get("s")
        posts = get_cached_list("posts", update_posts_cache, search)
        context = {"status": True, "posts": posts}
        logging.info(f"获取文章列表成功, 数量: {len(posts)}")
    except Exception as error:
        logging.error(repr(error))
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 获取所有页面 pub/get_pages
@csrf_exempt
@api_auth_required
def get_pages(request):
    """
    获取所有页面列表
    
    GET参数:
        s: 搜索关键词（可选）
        
    返回:
        {"status": True, "pages": [...]}
    """
    try:
        search = request.GET.get("s")
        pages = get_cached_list("pages", update_pages_cache, search)
        context = {"status": True, "pages": pages}
        logging.info(f"获取页面列表成功, 数量: {len(pages)}")
    except Exception as error:
        logging.error(repr(error))
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 获取所有配置 pub/get_configs
@csrf_exempt
@api_auth_required
def get_configs(request):
    """
    获取所有配置文件列表
    
    GET参数:
        s: 搜索关键词（可选）
        
    返回:
        {"status": True, "configs": [...]}
    """
    try:
        search = request.GET.get("s")
        configs = get_cached_list("configs", update_configs_cache, search)
        context = {"status": True, "configs": configs}
        logging.info(f"获取配置列表成功, 数量: {len(configs)}")
    except Exception as error:
        logging.error(repr(error))
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 获取所有图片 pub/get_images
@csrf_exempt
@api_auth_required
def get_images(request):
    """
    获取所有图片列表
    
    GET参数:
        s: 搜索关键词（可选）
        
    返回:
        {"status": True, "images": [...]}
    """
    try:
        search = request.GET.get("s")
        images_list = []
        # 优化：只查询需要的字段
        images = ImageModel.objects.only('name', 'size', 'url', 'date')
        
        # 优化：在数据库层面进行搜索过滤
        if search:
            from django.db.models import Q
            images = images.filter(Q(name__icontains=search) | Q(url__icontains=search))
        
        for i in images:
            images_list.append({
                "name": i.name,
                "size": convert_to_kb_mb_gb(int(i.size)),
                "url": escape(i.url),
                "date": strftime("%Y-%m-%d %H:%M:%S", localtime(float(i.date))),
                "time": i.date
            })
        
        images_list.sort(key=lambda x: x["time"], reverse=True)
        context = {"status": True, "images": images_list}
        logging.info(f"获取图片列表成功, 数量: {len(images_list)}")
    except Exception as error:
        logging.error(repr(error))
        context = {"status": False, "error": repr(error)}
    return JsonResponse(safe=False, data=context)


# 自动修复程序 pub/fix
@csrf_exempt
@api_auth_required
def auto_fix(request):
    """
    自动修复系统配置
    
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        counter = fix_all()
        msg = gettext("FIX_DISPLAY").format(counter)
        context = {"msg": msg, "status": True}
        logging.info(f"自动修复完成: {counter} 个字段")
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# ========================================
# 友链管理类 API (Friend Links Management APIs)
# ========================================

# 获取友情链接 pub/friends (公开接口，保留原有格式)
@csrf_exempt
def friends(request):
    """
    获取公开显示的友情链接列表
    无需鉴权，公开访问
    
    返回:
        {"data": [...], "status": True} - 保持原有格式以保证向后兼容
    """
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
        logging.info(f"获取公开友链成功, 数量: {len(data)}")
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)

# 获取全部友情链接 pub/get_friends (保留原有格式)
@csrf_exempt
@api_auth_required
def get_friends(request):
    """
    获取所有友情链接(包括隐藏的)
    
    GET参数:
        s: 搜索关键词(可选)
        
    返回:
        {"data": [...], "status": True} - 保持原有格式以保证向后兼容
    """
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
        logging.info(f"获取全部友链成功, 数量: {len(posts)}")
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 新增友链 pub/add_friend
@csrf_exempt
@api_auth_required
def add_friend(request):
    """
    新增友情链接
    
    POST参数:
        name: 名称
        url: 链接
        image: 图片URL
        description: 简介
        status: 状态("显示"/其他)
        
    返回:
        {"msg": "消息", "time": "", "status": True/False}
    """
    try:
        friend = FriendModel()
        friend.name = unicodedata.normalize('NFC', request.POST.get("name"))
        friend.url = unicodedata.normalize('NFC', request.POST.get("url"))
        friend.imageUrl = unicodedata.normalize('NFC', request.POST.get("image"))
        friend.description = unicodedata.normalize('NFC', request.POST.get("description"))
        friend.time = str(float(time()))
        friend.status = request.POST.get("status") == "显示"
        friend.save()
        context = {"msg": gettext("ADD_SUCCESS"), "time": friend.time, "status": True}
        logging.info(f"添加友链成功: {friend.name}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 编辑友链 pub/edit_friend
@csrf_exempt
@api_auth_required
def edit_friend(request):
    """
    编辑友情链接
    
    POST参数:
        time: 友链ID(时间戳)
        name: 名称
        url: 链接
        image: 图片URL
        description: 简介
        status: 状态("显示"/其他)
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.name = unicodedata.normalize('NFC', request.POST.get("name"))
        friend.url = unicodedata.normalize('NFC', request.POST.get("url"))
        friend.imageUrl = unicodedata.normalize('NFC', request.POST.get("image"))
        friend.description = unicodedata.normalize('NFC', request.POST.get("description"))
        friend.status = request.POST.get("status") == "显示"
        friend.save()
        context = {"msg": gettext("EDIT_SUCCESS"), "status": True}
        logging.info(f"编辑友链成功: {friend.name}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除友链 pub/del_friend
@csrf_exempt
@api_auth_required
def del_friend(request):
    """
    删除友情链接
    
    POST参数:
        time: 友链ID(时间戳)
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend_name = friend.name
        friend.delete()
        context = {"msg": gettext("DEL_SUCCESS"), "status": True}
        logging.info(f"删除友链成功: {friend_name}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 申请友链 pub/ask_friend (公开接口，保留原有格式)
@csrf_exempt
def ask_friend(request):
    """
    公开的友链申请接口
    包含reCAPTCHA人机验证
    
    POST参数:
        name: 名称
        url: 链接
        image: 图片URL
        description: 简介
        verify: reCAPTCHA验证token
        
    返回:
        {"msg": "消息", "time": "", "status": True/False} - 保持原有格式以保证向后兼容
    """
    try:
        if get_setting_cached("ALLOW_FRIEND") != "是":
            return HttpResponseForbidden()
        # 人机验证
        verify = request.POST.get("verify")
        token = get_setting_cached("RECAPTCHA_TOKEN")
        typ = get_setting_cached("FRIEND_RECAPTCHA")
        if typ == "v3":
            if verify:
                captcha = requests.get(
                    "https://recaptcha.google.cn/recaptcha/api/siteverify?secret=" + token + "&response=" + verify).json()
                logging.info("reCaptchaV3结果: " + str(captcha))
                if captcha["score"] <= 0.5:
                    return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
            else:
                logging.info("未收到人机验证信息")
                return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
        if typ == "v2":
            if verify:
                captcha = requests.get(
                    "https://recaptcha.google.cn/recaptcha/api/siteverify?secret=" + token + "&response=" + verify).json()
                logging.info("reCaptchaV2结果: " + str(captcha))
                if not captcha["success"]:
                    return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
            else:
                logging.info("未收到人机验证信息")
                return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
        # 通过验证
        friend = FriendModel()
        friend.name = unicodedata.normalize('NFC', request.POST.get("name"))
        friend.url = unicodedata.normalize('NFC', request.POST.get("url"))
        friend.imageUrl = unicodedata.normalize('NFC', request.POST.get("image"))
        friend.description = unicodedata.normalize('NFC', request.POST.get("description"))
        friend.time = str(float(time()))
        friend.status = False
        friend.save()
        CreateNotification("友链申请 " + friend.name,
                           "站点名: {}<br>链接: {}<br>图片: {}<br>简介: {}<br>".format(escapeString(friend.name), escapeString(friend.url),
                                                                                       escapeString(friend.imageUrl),
                                                                                       escapeString(friend.description)), time())
        context = {"msg": "申请成功！", "time": friend.time, "status": True}
        logging.info(f"友链申请成功: {friend.name} - {friend.url}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# ========================================
# 自定义字段类 API (Custom Fields APIs)
# ========================================

# 获取自定义字段 pub/get_custom (带鉴权和RestrictedPython沙箱)
@csrf_exempt
@api_auth_required
def get_custom(request):
    """
    获取并执行自定义字段内容
    
    安全策略:
    1. 强制需要API Token鉴权
    2. 使用RestrictedPython提供的沙箱环境
    3. 记录所有执行尝试
    
    GET/POST参数:
        key: 自定义字段名
        其他参数会作为变量传入执行环境
        
    返回:
        {"data": "输出内容", "status": True}
    """
    try:
        from RestrictedPython import compile_restricted, safe_globals, limited_builtins, utility_builtins
        from RestrictedPython.Eval import default_guarded_getitem
        
        key = request.GET.get("key") if request.GET.get("key") else request.POST.get("key")
        custom_field = CustomModel.objects.get(name=key)
        func_str = custom_field.content
        
        # 构建参数字典
        body = request.GET.copy()
        body.update(request.POST)
        body = dict(body)
        for k in body.keys():
            if len(body[k]) == 1:
                body[k] = body[k][0]
        
        # RestrictedPython 安全环境
        restricted_globals = {
            '__builtins__': {
                **limited_builtins,
                **utility_builtins,
                '_getitem_': default_guarded_getitem,
                'json': json,
                'print': print,
            }
        }
        restricted_globals.update(safe_globals)
        restricted_globals.update(body)
        
        # 捕获输出
        old_stdout = sys.stdout
        output = sys.stdout = StringIO()
        
        try:
            # 使用 RestrictedPython 编译代码
            byte_code = compile_restricted(func_str, filename='<custom_field>', mode='exec')
            
            if byte_code.errors:
                # 编译错误
                error_msg = '\n'.join(byte_code.errors)
                logging.warning(f"自定义字段编译错误: {custom_field.name} - {error_msg}")
                print(f"编译错误: {error_msg}")
            else:
                # 执行编译后的代码
                exec(byte_code.code, restricted_globals)
        except Exception as e:
            # 执行错误，尝试作为表达式处理
            try:
                byte_code = compile_restricted(func_str, filename='<custom_field>', mode='eval')
                if byte_code.errors:
                    print(func_str)
                else:
                    result = eval(byte_code.code, restricted_globals)
                    print(result)
            except Exception:
                # 都失败则直接输出内容
                print(func_str)
        
        sys.stdout = old_stdout
        context = {"data": output.getvalue(), "status": True}
        logging.info(f"执行自定义字段: {custom_field.name}")
    except Exception as error:
        logging.error(f"自定义字段执行错误: {repr(error)}")
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 编辑自定义字段 pub/set_custom
@csrf_exempt
@api_auth_required
def set_custom(request):
    """
    编辑自定义字段内容
    
    POST参数:
        name: 字段名
        content: 字段内容
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        name = unicodedata.normalize('NFC', request.POST.get("name"))
        content = unicodedata.normalize('NFC', request.POST.get("content"))
        save_custom(name, content)
        context = {"msg": gettext("SAVE_SUCCESS"), "status": True}
        logging.info(f"保存自定义字段: {name}")
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除自定义的字段 pub/del_custom
@csrf_exempt
@api_auth_required
def del_custom(request):
    """
    删除自定义字段
    
    POST参数:
        name: 字段名
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        name = request.POST.get("name")
        CustomModel.objects.filter(name=name).delete()
        context = {"msg": gettext("DEL_SUCCESS"), "status": True}
        logging.info(f"删除自定义字段: {name}")
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 新建自定义的字段 pub/new_custom
@csrf_exempt
@api_auth_required
def new_custom(request):
    """
    新建自定义字段
    
    POST参数:
        name: 字段名
        content: 字段内容
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        name = unicodedata.normalize('NFC', request.POST.get("name"))
        content = unicodedata.normalize('NFC', request.POST.get("content"))
        save_custom(name, content)
        context = {"msg": gettext("SAVE_SUCCESS"), "status": True}
        logging.info(f"创建自定义字段: {name}")
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# ========================================
# 通知和统计类 API (Notification and Statistics APIs)
# ========================================

# 获取全部消息 pub/get_notifications
@csrf_exempt
@api_auth_required
def get_notifications(request):
    """
    获取所有通知消息
    
    返回:
        {"data": [...], "status": True}
    """
    try:
        context = {"data": GetNotifications(), "status": True}
        logging.info("获取通知列表成功")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取博客基本信息 pub/status (公开接口,保留原有格式)
@csrf_exempt
def status(request):
    """
    获取博客基本状态信息
    无需鉴权，公开访问
    
    返回:
        {"data": {"posts": "", "last": ""}, "status": True} - 保持原有格式以保证向后兼容
    """
    try:
        cache_obj = Cache.objects.filter(name="posts").first()
        if cache_obj:
            posts = json.loads(cache_obj.content)
        else:
            posts = update_posts_cache()
        if not posts:
            posts = []
        posts_count = len(posts)
        last = get_setting_cached("LAST_LOGIN")
        context = {"data": {"posts": str(posts_count), "last": last}, "status": True}
        logging.info(f"获取博客状态成功: {posts_count} 篇文章")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 统计API pub/statistic (公开接口,保留原有格式)
@csrf_exempt
def statistic(request):
    """
    页面访问统计API
    基于域名白名单验证
    
    返回:
        {"site_pv": int, "page_pv": int, "site_uv": int, "status": True} - 保持原有格式以保证向后兼容
    """
    try:
        # 使用通用验证函数
        is_valid, domain_name, referer = validate_statistic_domain(request)
        if not is_valid:
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
@api_auth_required
def notifications(request):
    """
    创建自定义通知
    
    POST参数(JSON Body):
        title: 通知标题
        content: 通知内容
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        data = json.loads(request.body.decode())
        content = unicodedata.normalize('NFC', data.get('content'))
        title = unicodedata.normalize('NFC', data.get('title'))
        CreateNotification(title, content, time())
        logging.info(f"创建通知成功: {title}")
        return JsonResponse(safe=False, data={"msg": gettext("ADD_SUCCESS"), "status": True})
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
        return JsonResponse(safe=False, data=context)


# ========================================
# 说说管理类 API (Talks Management APIs)
# ========================================

# 获取说说 pub/talks (公开接口,保留原有格式)
@csrf_exempt
def get_talks(request):
    """
    获取说说列表(分页)
    无需鉴权，公开访问
    
    GET参数:
        page: 页码(默认1)
        limit: 每页数量(默认5)
        
    返回:
        {"msg": "消息", "status": True, "count": int, "data": [...]} - 保持原有格式以保证向后兼容
    """
    try:
        page = int(request.GET.get('page')) if request.GET.get('page') else 1
        limit = int(request.GET.get('limit')) if request.GET.get('limit') else 5
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', '')
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
        logging.info(f"获取说说列表成功, 页码: {page}, 数量: {len(talks)}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 点赞说说 pub/like_talk (公开接口,保留原有格式)
@csrf_exempt
def like_talk(request):
    """
    点赞/取消点赞说说
    无需鉴权，公开访问
    通过IP地址防止重复点赞
    
    POST参数:
        id: 说说ID
        
    返回:
        {"msg": "消息", "action": True/False, "status": True} - 保持原有格式以保证向后兼容
        action: True表示点赞，False表示取消点赞
    """
    try:
        talk_id = request.POST.get('id')
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', '')
        talk = TalkModel.objects.get(id=uuid.UUID(hex=talk_id))
        t = json.loads(talk.like)
        if ip in t:
            t.remove(ip)
            talk.like = json.dumps(t)
            talk.save()
            logging.info(f"{ip} 取消点赞: {talk_id}")
            context = {"msg": "取消成功！", "action": False, "status": True}
        else:
            t.append(ip)
            talk.like = json.dumps(t)
            talk.save()
            logging.info(f"{ip} 成功点赞: {talk_id}")
            context = {"msg": "点赞成功！", "action": True, "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存说说 pub/save_talk
@csrf_exempt
@api_auth_required
def save_talk(request):
    """
    保存/编辑说说
    
    POST参数:
        id: 说说ID(编辑时提供)
        content: 内容
        tags: 标签(JSON数组字符串)
        time: 时间戳(编辑时使用)
        values: 附加字段(JSON字符串)
        
    返回:
        {"msg": "消息", "status": True, "id": ""}
    """
    try:
        context = {"msg": gettext("SAVE_SUCCESS"), "status": True}
        if request.POST.get("id"):
            talk = TalkModel.objects.get(id=uuid.UUID(hex=request.POST.get("id")))
            talk.content = unicodedata.normalize('NFC', request.POST.get("content"))
            talk.tags = request.POST.get("tags")
            talk.time = request.POST.get("time")
            talk.values = request.POST.get("values")
            talk.save()
            context["msg"] = gettext("EDIT_SUCCESS")
            logging.info(f"编辑说说成功: {talk.id.hex}")
        else:
            talk = TalkModel(content=unicodedata.normalize('NFC', request.POST.get("content")),
                             tags=request.POST.get("tags"),
                             time=str(int(time())),
                             like="[]",
                             values=request.POST.get("values"))
            talk.save()
            context["id"] = talk.id.hex
            logging.info(f"创建说说成功: {talk.id.hex}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除说说 pub/del_talk
@csrf_exempt
@api_auth_required
def del_talk(request):
    """
    删除说说
    
    POST参数:
        id: 说说ID
        
    返回:
        {"msg": "消息", "status": True/False}
    """
    try:
        talk_id = request.POST.get("id")
        TalkModel.objects.get(id=uuid.UUID(hex=talk_id)).delete()
        context = {"msg": gettext("DEL_SUCCESS"), "status": True}
        logging.info(f"删除说说成功: {talk_id}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)

# 获取全部说说 pub/get_all_talks
@csrf_exempt
@api_auth_required
def get_all_talks(request):
    """
    获取所有说说(管理用)
    
    GET参数:
        s: 搜索关键词(可选)
        
    返回:
        {"msg": "消息", "status": True, "data": [...]}
    """
    try:
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
        context = {"msg": gettext("GET_SUCCESS"), "status": True, "data": sorted(posts, key=lambda x: x["time"], reverse=True)}
        logging.info(f"获取全部说说成功, 数量: {len(posts)}")
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)