import random
import sys
import uuid

from io import StringIO
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hexoweb.libs.image import get_image_host, delete_image
from .functions import *


# 登录验证API api/auth
def auth(request):
    captcha = "获取失败"
    try:
        username = request.POST.get("username")
        password = request.POST.get("password")
        verify = request.POST.get("verify")
        if request.POST.get("type") == "v3":
            token = get_setting("LOGIN_RECAPTCHA_SERVER_TOKEN")
            if verify:
                captcha = requests.get(
                    "https://recaptcha.google.cn/recaptcha/api/siteverify?secret=" + token + "&response=" + verify).json()
                if captcha["score"] <= 0.5:
                    logging.info("reCaptchaV3结果: " + str(captcha))
                    return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
            else:
                logging.info("未收到人机验证信息")
                return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
        elif request.POST.get("type") == "v2":
            token = get_setting("LOGIN_RECAPTCHAV2_SERVER_TOKEN")
            if verify:
                captcha = requests.get(
                    "https://recaptcha.google.cn/recaptcha/api/siteverify?secret=" + token + "&response=" + verify).json()
                if not captcha["success"]:
                    logging.info("reCaptchaV2结果: " + str(captcha))
                    return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
            else:
                logging.info("未收到人机验证信息")
                return JsonResponse(safe=False, data={"msg": "人机验证失败！", "status": False})
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            context = {"msg": "登录成功，等待转跳", "status": True}
        else:
            context = {"msg": "登录信息错误", "status": False}
    except Exception as e:
        logging.error(repr(e))
        logging.info("reCaptcha结果: " + str(captcha))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 Hexo Provider 配置 api/set_hexo
@login_required(login_url="/login/")
def set_hexo(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        provider = unicodedata.normalize('NFC', request.POST.get('provider'))
        config = json.loads(provider)["params"]["config"]
        verify = {"status": -1}
        msg = ""
        force = request.POST.get("force") == "true"
        if config == "Hexo" and not force:
            verify = verify_provider(json.loads(provider))
            msg = ""
            if verify["status"] == -1:
                return JsonResponse(safe=False, data={"msg": "远程连接错误!请检查Token", "status": False})
            if verify["hexo"]:
                msg += "检测到Hexo版本: " + verify["hexo"]
            else:
                msg += "未检测到Hexo"
            if verify["indexhtml"]:
                msg += "\n检测到index.html, 这可能不是正确的仓库"
            if verify["config_hexo"]:
                msg += "\n检测到Hexo配置文件"
            else:
                msg += "\n未检测到Hexo配置"
            if verify["theme"]:
                msg += "\n检测到主题: " + verify["theme"]
            else:
                msg += "\n未检测到主题"
            if verify["config_theme"]:
                msg += "\n检测到主题配置" + verify["config_theme"]
            else:
                msg += "\n未检测到主题配置"
            if verify["theme_dir"]:
                msg += "\n检测到主题目录"
            else:
                msg += "\n未检测到主题目录"
            if verify["package"]:
                msg += "\n检测到package.json"
            else:
                msg += "\n未检测到package.json"
            if verify["source"]:
                msg += "\n检测到source目录 "
            else:
                msg += "\n未检测到source目录"
            msg = msg.replace("\n", "<br>")
        if verify["status"] > 0 or config != "Hexo" or force:
            save_setting("PROVIDER", provider)
            update_provider()
            delete_all_caches()
            del_all_postmark()
            context = {"msg": msg + "\n保存配置成功!", "status": True}
        else:
            context = {"msg": msg + "\n配置校验失败", "status": False}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 OnePush api/set_onepush
@login_required(login_url="/login/")
def set_onepush(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        onepush = request.POST.get("onepush")
        save_setting("ONEPUSH", onepush)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 测试 OnePush api/test_onepush
@login_required(login_url="/login/")
def test_onepush(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        onepush = json.loads(request.POST.get("onepush"))
        ntfy = notify(onepush["notifier"], **onepush["params"], title="Qexo消息测试",
                      content="如果你收到了这则消息, 那么代表您的消息配置成功了")
        try:
            data = ntfy.text
        except Exception:
            data = "OK"
        context = {"msg": data, "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置API api/setapi
@login_required(login_url="/login/")
def set_api(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        apikey = request.POST.get("apikey")
        if apikey:
            save_setting("WEBHOOK_APIKEY", apikey)
        else:
            if not SettingModel.objects.filter(name="WEBHOOK_APIKEY").count():
                save_setting("WEBHOOK_APIKEY", ''.join(
                    random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12)))
        save_setting("ALLOW_FRIEND", request.POST.get("allow_friend"))
        save_setting("FRIEND_RECAPTCHA", request.POST.get("friend-recaptcha"))
        save_setting("RECAPTCHA_TOKEN", request.POST.get("recaptcha-token"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 安全设置 api/et_security
@login_required(login_url="/login/")
def set_security(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        save_setting("LOGIN_RECAPTCHA_SERVER_TOKEN", request.POST.get("server-token"))
        save_setting("LOGIN_RECAPTCHA_SITE_TOKEN", request.POST.get("site-token"))
        save_setting("LOGIN_RECAPTCHAV2_SERVER_TOKEN", request.POST.get("server-token-v2"))
        save_setting("LOGIN_RECAPTCHAV2_SITE_TOKEN", request.POST.get("site-token-v2"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置图床配置 api/set_image_host
@login_required(login_url="/login/")
def set_image_host(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        image_host = request.POST.get("image_host")
        save_setting("IMG_HOST", image_host)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 Abbrlink 配置 api/set_abbrlink
@login_required(login_url="/login/")
def set_abbrlink(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        alg = request.POST.get("alg")
        rep = request.POST.get("rep")
        save_setting("ABBRLINK_ALG", alg)
        save_setting("ABBRLINK_REP", rep)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置CDN api/set_cdn
@login_required(login_url="/login/")
def set_cdn(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        cdn_prev = request.POST.get("cdn")
        save_setting("CDN_PREV", cdn_prev)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置自定义配置 api/set_cust
@login_required(login_url="/login/")
def set_cust(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        site_name = request.POST.get("name")
        split_word = request.POST.get("split")
        logo = request.POST.get("logo")
        icon = request.POST.get("icon")
        logo_dark = request.POST.get("logo-dark")
        save_setting("QEXO_NAME", site_name)
        save_setting("QEXO_SPLIT", split_word)
        save_setting("QEXO_LOGO", logo)
        save_setting("QEXO_ICON", icon)
        save_setting("QEXO_LOGO_DARK", logo_dark)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置用户信息 api/set_user
@login_required(login_url="/login/")
def set_user(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        password = request.POST.get("password")
        username = request.POST.get("username")
        newpassword = request.POST.get("newpassword")
        repassword = request.POST.get("repassword")
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            if repassword != newpassword:
                context = {"msg": "两次密码不一致!", "status": False}
                return JsonResponse(safe=False, data=context)
            if not newpassword:
                context = {"msg": "请输入正确的密码！", "status": False}
                return JsonResponse(safe=False, data=context)
            if not username:
                context = {"msg": "请输入正确的用户名！", "status": False}
                return JsonResponse(safe=False, data=context)
            u = User.objects.get(username__exact=request.user.username)
            u.delete()
            User.objects.create_superuser(username=username, password=newpassword)
            context = {"msg": "保存成功！请重新登录", "status": True}
        else:
            context = {"msg": "原密码错误!", "status": False}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置统计配置 api/set_statistic
@login_required(login_url="/login/")
def set_statistic(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        domains = request.POST.get("statistic_domains")
        allow = request.POST.get("allow_statistic")
        save_setting("STATISTIC_ALLOW", allow)
        save_setting("STATISTIC_DOMAINS", domains)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 CustomModel 的字段 api/set_custom
@login_required(login_url="/login/")
def set_custom(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        save_custom(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 CustomModel 的字段 api/del_custom
@login_required(login_url="/login/")
def del_custom(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        CustomModel.objects.filter(name=request.POST.get("name")).delete()
        context = {"msg": "删除成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 新建 CustomModel 的字段 api/new_custom
@login_required(login_url="/login/")
def new_custom(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        save_custom(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 SettingsModel 的字段 api/set_value
@login_required(login_url="/login/")
def set_value(request):
    try:
        save_setting(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置 SettingsModel 的字段 api/del_value
@login_required(login_url="/login/")
def del_value(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        SettingModel.objects.filter(name=request.POST.get("name")).delete()
        context = {"msg": "删除成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 新建 SettingsModel 的字段 api/new_value
@login_required(login_url="/login/")
def new_value(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        save_setting(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 自动修复程序 api/fix
@login_required(login_url="/login/")
def auto_fix(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        counter = fix_all()
        msg = "尝试自动修复了 {} 个字段，请在稍后检查和修改配置".format(counter)
        context = {"msg": msg, "status": True}
    except Exception as e:
        logging.error(repr(e))
        context = {"msg": repr(e), "status": False}
    return JsonResponse(safe=False, data=context)


# 执行更新 api/do_update
@login_required(login_url="/login/")
def do_update(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    branch = request.POST.get("branch")
    try:
        url = get_update_url(branch)
        if not url:
            context = {"msg": "无此更新通道", "status": False}
            return JsonResponse(safe=False, data=context)
        if check_if_vercel():
            res = VercelOnekeyUpdate(url)
        else:
            res = LocalOnekeyUpdate(url)
            save_setting("UPDATE_FROM", QEXO_VERSION)
            return JsonResponse(safe=False, data=res)
        if res["status"]:
            save_setting("UPDATE_FROM", QEXO_VERSION)
            context = {"msg": "更新成功，请等待自动部署!", "status": True}
        else:
            context = {"msg": res["msg"], "status": False}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存内容 api/save
@login_required(login_url="/login/")
def save(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        content = unicodedata.normalize('NFC', request.POST.get('content'))
        flag = False
        for i in Provider().config["configs"]["type"]:
            if file_path.endswith(i):
                flag = True
                break
        if (not request.user.is_staff) and flag:
            logging.info(f"子用户{request.user.username}尝试修改{file_path}被拒绝")
            return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
        commitchange = f"Update Post Draft {file_path} by Qexo"
        try:
            if Provider().save(file_path, content, commitchange):
                context = {"msg": "保存成功并提交部署！", "status": True}
            else:
                context = {"msg": "保存成功！", "status": True}
            delete_all_caches()
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存文章 api/save_post
@login_required(login_url="/login/")
def save_post(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_name = unicodedata.normalize('NFC', request.POST.get('file'))
        content = unicodedata.normalize('NFC', request.POST.get('content'))
        front_matter = json.loads(unicodedata.normalize('NFC', request.POST.get('front_matter')))
        try:
            _front_matter = "---\n{}---".format(yaml.dump(front_matter, allow_unicode=True))
            if not content.startswith("\n"):
                _front_matter += "\n"
            result = Provider().save_post(file_name, _front_matter + content, path=request.POST.get("path"), status=True)
            if result[0]:
                context = {"msg": "保存成功并提交部署！", "status": True, "path": result[1]}
            else:
                context = {"msg": "保存成功！", "status": True, "path": result[1]}
            mark_post(result[1], front_matter, True, file_name)
            if result[2]:
                del_postmark(result[2])
            delete_all_caches()
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存页面 api/save_page
@login_required(login_url="/login/")
def save_page(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        content = unicodedata.normalize('NFC', request.POST.get('content'))
        front_matter = json.loads(unicodedata.normalize('NFC', request.POST.get('front_matter')))
        commitchange = f"Update Page {file_path}"
        try:
            front_matter = "---\n{}---".format(yaml.dump(front_matter, allow_unicode=True))
            if not content.startswith("\n"):
                front_matter += "\n"
            if Provider().save(file_path, front_matter + content, commitchange):
                context = {"msg": "保存成功并提交部署！", "status": True}
            else:
                context = {"msg": "保存成功！", "status": True}
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存页面 api/new_page
@login_required(login_url="/login/")
def new_page(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        content = unicodedata.normalize('NFC', request.POST.get('content'))
        front_matter = json.loads(unicodedata.normalize('NFC', request.POST.get('front_matter')))
        try:
            front_matter = "---\n{}---".format(yaml.dump(front_matter, allow_unicode=True))
            if not content.startswith("\n"):
                front_matter += "\n"
            result = Provider().save_page(file_path, front_matter + content)
            if result[0]:
                context = {"msg": "保存成功并提交部署！", "status": True, "path": result[1]}
            else:
                context = {"msg": "保存成功！", "status": True, "path": result[1]}
            delete_all_caches()
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存草稿 api/save_draft
@login_required(login_url="/login/")
def save_draft(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_name = unicodedata.normalize('NFC', request.POST.get('file'))
        content = unicodedata.normalize('NFC', request.POST.get('content'))
        front_matter = json.loads(unicodedata.normalize('NFC', request.POST.get('front_matter')))
        try:
            # 创建/更新草稿
            _front_matter = "---\n{}---".format(yaml.dump(front_matter, allow_unicode=True))
            if not content.startswith("\n"):
                _front_matter += "\n"
            result = Provider().save_post(file_name, _front_matter + content, path=request.POST.get("path"), status=False)
            if result[0]:
                context = {"msg": "保存草稿成功并提交部署！", "status": True, "path": result[1]}
            else:
                context = {"msg": "保存草稿成功！", "status": True, "path": result[1]}
            mark_post(result[1], front_matter, False, file_name)
            delete_all_caches()
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除内容 api/delete
@login_required(login_url="/login/")
def delete(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        if (not request.user.is_staff) and file_path[:4] in ["yaml", ".yml"]:
            logging.info(f"子用户{request.user.username}尝试删除{file_path}被拒绝")
            return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
        commitchange = f"Delete {file_path} by Qexo"
        try:
            if Provider().delete(file_path, commitchange):
                context = {"msg": "删除成功并提交部署！", "status": True}
            else:
                context = {"msg": "删除成功！", "status": True}
            # Delete Caches
            delete_all_caches()
            try:
                PostModel.objects.filter(path=file_path).delete()
            except:
                pass
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error)}
    return JsonResponse(safe=False, data=context)


# 重命名文件 api/rename
@login_required(login_url="/login/")
def rename(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = unicodedata.normalize('NFC', request.POST.get('file'))
        new_path = unicodedata.normalize('NFC', request.POST.get('new'))
        if (not request.user.is_staff) and file_path[:4] in ["yaml", ".yml"]:
            logging.info(f"子用户{request.user.username}尝试重命名{file_path}被拒绝")
            return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
        commitchange = f"Rename {file_path} by Qexo"
        try:
            if Provider().rename(file_path, new_path, commitchange):
                context = {"msg": "重命名成功并提交部署！", "status": True}
            else:
                context = {"msg": "重命名成功！", "status": True}
            # Delete Caches
            delete_all_caches()
            try:
                PostModel.objects.filter(path=file_path).delete()
            except:
                pass
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error)}
    return JsonResponse(safe=False, data=context)


# 删除图片记录 api/delete_img
@login_required(login_url="/login/")
def delete_img(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        image_date = request.POST.get('image')
        try:
            image = ImageModel.objects.filter(date=image_date)
            msg = "已删除本地记录"
            if request.POST.get("sync") == "true" and image[0].deleteConfig:
                msg = delete_image(json.loads(image[0].deleteConfig))
            image.delete()
            context = {"msg": msg, "status": True}
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 清除缓存 api/purge
@login_required(login_url="/login/")
def purge(request):
    try:
        delete_all_caches()
        context = {"msg": "清除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 自动设置 Webhook 事件 api/create_webhook
@login_required(login_url="/login/")
def create_webhook_config(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
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
            if Provider().delete_hooks():
                Provider().create_hook(config)
                context = {"msg": "设置成功！", "status": True}
            else:
                context = {"msg": "服务商不支持！", "status": False}
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# Webhook api/webhook
@csrf_exempt
def webhook(request):
    try:
        if request.GET.get("token") == get_setting("WEBHOOK_APIKEY"):
            delete_all_caches()
            context = {"msg": "操作成功！", "status": True}
        else:
            context = {"msg": "校验错误", "status": False}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 上传图片 api/upload
@csrf_exempt
@login_required(login_url="/login/")
def upload_img(request):
    context = dict(msg="上传失败！", url=False)
    if request.method == "POST":
        file = request.FILES.getlist('file[]')[0] if request.FILES.getlist('file[]') else request.FILES.getlist('file')[0]
        try:
            image_host = json.loads(get_setting("IMG_HOST"))
            if image_host["type"] != "关闭":
                res = get_image_host(image_host["type"], **image_host["params"]).upload(file)
                context["url"] = res[0]
                context["status"] = True
                context["msg"] = "上传成功"
                image = ImageModel()
                image.name = file.name
                image.url = context["url"]
                image.size = file.size
                image.type = file.content_type
                image.date = time()
                image.deleteConfig = json.dumps(res[1])
                image.save()
                context["data"] = {"name": image.name, "size": convert_to_kb_mb_gb(int(image.size)), "url": escape(image.url),
                                   "date": strftime("%Y-%m-%d %H:%M:%S", localtime(float(image.date))),
                                   "time": str(image.date)}
        except Exception as error:
            logging.error(repr(error))
            context = {"msg": repr(error), "url": False, "status": False}
    return JsonResponse(safe=False, data=context)


# 添加友链 api/add_friend
@login_required(login_url="/login/")
def add_friend(request):
    try:
        friend = FriendModel()
        friend.name = request.POST.get("name")
        friend.url = request.POST.get("url")
        friend.imageUrl = request.POST.get("image")
        friend.description = request.POST.get("description")
        friend.time = str(time())
        friend.status = request.POST.get("status") == "显示"
        friend.save()
        context = {"msg": "添加成功！", "time": friend.time, "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 修改友链 api/edit_friend
@login_required(login_url="/login/")
def edit_friend(request):
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


# 清理隐藏友链 api/clean_friend
@login_required(login_url="/login/")
def clean_friend(request):
    try:
        counter = 0
        all_friends = FriendModel.objects.filter(status__in=[False])
        for friend in all_friends:
            friend.delete()
            counter += 1
        context = {"msg": "成功清理了{}条友链".format(counter) if counter else "无隐藏的友链", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除友链 api/del_friend
@login_required(login_url="/login/")
def del_friend(request):
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 获取全部消息 api/get_notifications
@login_required(login_url="/login/")
def get_notifications(request):
    try:
        # 检查更新
        latest = get_latest_version()
        latest["newer_text"] = latest["newer_text"].replace("<h2>", "<h5>")
        if latest["status"]:
            cache = Cache.objects.filter(name="update")
            if cache.count():
                if (cache.first().content != latest["newer_time"]) and latest["hasNew"]:
                    CreateNotification("程序更新", "检测到更新: " + latest["newer"] + "<br>" + latest[
                        "newer_text"] + "<p>可前往 <object><a href=\"/settings.html\">设置</a></object> 在线更新</p>",
                                       time())
                    update_caches("update", latest["newer_time"], "text")
            else:
                if latest["hasNew"]:
                    CreateNotification("程序更新", "检测到更新: " + latest["newer"] + "<br>" + latest[
                        "newer_text"] + "<p>可前往 <object><a href=\"/settings.html\">设置</a></object> 在线更新</p>",
                                       time())
                    update_caches("update", latest["newer_time"], "text")
        context = {"data": GetNotifications(), "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 删除指定消息 api/del_notifications
@login_required(login_url="/login/")
def del_notification(request):
    try:
        DelNotification(request.POST.get("time"))
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 清理全部消息 api/clear_notifications
@login_required(login_url="/login/")
def clear_notification(request):
    try:
        all_notify = NotificationModel.objects.all()
        for N in all_notify:
            N.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置文章/页面侧边栏 api/set_sidebar
@login_required(login_url="/login/")
def set_sidebar(request):
    try:
        typ = request.POST.get("type")
        if typ == "page":
            save_setting("PAGE_SIDEBAR", request.POST.get("content"))
        elif typ == "post":
            save_setting("POST_SIDEBAR", request.POST.get("content"))
        elif typ == "talk":
            save_setting("TALK_SIDEBAR", request.POST.get("content"))
        else:
            raise "未知侧边栏"
        context = {"msg": "修改成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 设置文章页面自动截取 api/set_excerpt
@login_required(login_url="/login/")
def set_excerpt(request):
    try:
        excerpt = request.POST.get("excerpt")
        save_setting("AUTO_EXCERPT_CONFIG", excerpt)
        context = {"msg": "修改成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 保存说说 api/save_talk
@login_required(login_url="/login/")
def save_talk(request):
    try:
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


# 删除说说 api/del_talk
@login_required(login_url="/login/")
def del_talk(request):
    try:
        TalkModel.objects.get(id=uuid.UUID(hex=request.POST.get("id"))).delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)


# 运行云端命令
@login_required(login_url="/login/")
def run_online_script(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return JsonResponse(safe=False, data={"msg": "子用户不支持此操作！", "status": False})
    try:
        path = request.POST.get("path")
        if path:
            remote_script = requests.get("https://raw.githubusercontent.com/Qexo/Scripts/main/" + path).text
            logging.info("执行云端命令: " + path)
            old_stdout = sys.stdout
            output = sys.stdout = StringIO()
            locals().update(json.loads(request.POST.get("argv")))
            exec(remote_script)
            sys.stdout = old_stdout
            logging.info(f"执行{path}成功: " + output.getvalue().rstrip())
            context = {"msg": "运行成功！", "data": output.getvalue(), "status": True}
        else:
            context = {"msg": "请输入正确的参数！", "status": False}
    except Exception as error:
        logging.error(repr(error))
        context = {"msg": repr(error), "status": False}
    return JsonResponse(safe=False, data=context)
