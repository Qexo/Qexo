# -*- encoding: utf-8 -*-
import uuid
from math import ceil
from urllib.parse import quote, unquote

from django import template
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader

from hexoweb.libs.image import all_providers as all_image_providers
from hexoweb.libs.image import get_params as get_image_params
from hexoweb.libs.onepush import all_providers as onepush_providers
from hexoweb.libs.onepush import get_notifier
from hexoweb.libs.platforms import all_providers, get_params
from hexoweb.libs.platforms import all_configs as platform_configs
from .api import *


def page_404(request, exception):
    return render(request, 'home/page-404.html', {"cdn_prev": "https://unpkg.com/"})


def page_403(request, exception):
    return render(request, 'home/page-403.html', {"cdn_prev": "https://unpkg.com/"})


def page_500(request):
    return render(request, 'home/page-500.html',
                  {"error": "程序遇到了错误！", "cdn_prev": "https://unpkg.com/"})


def login_view(request):
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info("未完成初始化配置, 转跳到初始化页面")
            return redirect("/init/")
    except Exception:
        logging.info("未检测到初始化配置, 转跳到初始化页面")
        return redirect("/init/")
    if request.user.is_authenticated:
        if not request.GET.get("next"):
            return redirect("/")
        else:
            return redirect(unquote(request.GET.get("next")))
    context = get_custom_config()
    site_token = get_setting("LOGIN_RECAPTCHA_SITE_TOKEN")
    server_token = get_setting("LOGIN_RECAPTCHA_SERVER_TOKEN")
    site_token_v2 = get_setting("LOGIN_RECAPTCHAV2_SITE_TOKEN")
    server_token_v2 = get_setting("LOGIN_RECAPTCHAV2_SERVER_TOKEN")
    if site_token and server_token:
        context["site_token"] = site_token
    if site_token_v2 and server_token_v2 and not context.get("site_token"):
        context["site_token_v2"] = site_token_v2
    return render(request, "accounts/login.html", context)


@login_required(login_url="/login/")
def update_view(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return page_403(request, "您没有权限访问此页面")
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info("未完成初始化配置, 转跳到初始化页面")
            return redirect("/init/")
    except Exception:
        logging.info("未检测到初始化配置, 转跳到初始化页面")
        return redirect("/init/")
    if request.method == 'POST':
        for setting in request.POST.keys():
            save_setting(setting, request.POST.get(setting))
            if setting == "PROVIDER":
                update_provider()
        delete_all_caches()
    already = list()
    settings = SettingModel.objects.all()
    for query in settings:
        if query.name not in already:
            already.append(query.name)
    context = get_custom_config()
    context["settings"] = list()
    context["counter"] = 0
    for setting in ALL_SETTINGS:
        if setting[0] not in already:
            if setting[0] == "PROVIDER":  # migrate from 1.x
                _provider = {"provider": "github",
                             "params": {"token": get_setting("GH_TOKEN"),
                                        "branch": get_setting("GH_REPO_BRANCH"),
                                        "repo": get_setting("GH_REPO"),
                                        "path": get_setting("GH_PATH")}}
                context["settings"].append(dict(name=setting[0], value=json.dumps(_provider),
                                                placeholder=setting[3]))
                if verify_provider(_provider)["status"] == 1:
                    save_setting("PROVIDER", _provider)
                else:
                    context["msg"] = "自动生成PROVIDER错误，请检查配置并提交"

            else:
                if setting[2]:
                    save_setting(setting[0], setting[1])
                context["settings"].append(dict(name=setting[0], value=setting[1], placeholder=setting[3]))

            context["counter"] += 1
    if not context["counter"]:
        save_setting("JUMP_UPDATE", "false")
        return redirect("/")
    return render(request, "accounts/update.html", context)


def init_view(request):
    msg = None
    context = dict()
    context.update(get_custom_config())
    step = get_setting("INIT")
    if not step:
        save_setting("INIT", "1")
        step = "1"
    provider = False
    if step == "2" and User.objects.all():
        step = "3"
        save_setting("INIT", "3")
    if request.method == "POST":
        if request.POST.get("step") == "1":
            fix_all()
            save_setting("INIT", "2")
            if not User.objects.all():
                step = "2"
            else:
                step = "3"
                context["PROVIDER"] = get_setting("PROVIDER")
                # Get Provider Settings
                all_provider = all_providers()
                context["all_providers"] = dict()
                for provider in all_provider:
                    params = get_params(provider)
                    context["all_providers"][provider] = params
                context["all_platform_configs"] = platform_configs()
        if request.POST.get("step") == "2":
            username = request.POST.get("username")
            password = request.POST.get("password")
            repassword = request.POST.get("repassword")
            apikey = request.POST.get("apikey")
            try:
                if apikey:
                    save_setting("WEBHOOK_APIKEY", apikey)
                else:
                    if not SettingModel.objects.filter(name="WEBHOOK_APIKEY").count():
                        save_setting("WEBHOOK_APIKEY", ''.join(
                            random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in
                            range(12)))
                if repassword != password:
                    msg = "两次密码不一致!"
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                    context["apikey"] = apikey
                elif not password:
                    msg = "请输入正确的密码！"
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                    context["apikey"] = apikey
                elif not username:
                    msg = "请输入正确的用户名！"
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                    context["apikey"] = apikey
                else:
                    User.objects.create_superuser(username=username, password=password)
                    save_setting("INIT", "3")
                    step = "3"
                    context["PROVIDER"] = get_setting("PROVIDER")
                    # Get Provider Settings
                    all_provider = all_providers()
                    context["all_providers"] = dict()
                    for provider in all_provider:
                        params = get_params(provider)
                        context["all_providers"][provider] = params
                    context["all_platform_configs"] = platform_configs()
            except Exception as e:
                logging.error("初始化用户名密码错误:" + repr(e))
                msg = repr(e)
                context["username"] = username
                context["password"] = password
                context["repassword"] = repassword
        if request.POST.get("step") == "3":
            try:
                provider = {
                    "provider": request.POST.get("provider"),
                    "params": dict(request.POST)
                }
                if "provider" in provider["params"]:
                    del provider["params"]["provider"]
                if "step" in provider["params"]:
                    del provider["params"]["step"]
                if "csrfmiddlewaretoken" in provider["params"]:
                    del provider["params"]["csrfmiddlewaretoken"]
                for key in provider["params"].keys():
                    provider["params"][key] = provider["params"][key][0]
                if provider["params"]["config"] != "Hexo":
                    provider["params"]["_force"] = True
                if provider["params"].get("_force") is None:
                    verify = verify_provider(provider)
                    if verify["status"] and verify["status"] != -1:
                        save_setting("PROVIDER", json.dumps(provider))
                        update_provider()
                        step = "5" if check_if_vercel() else "6"
                        save_setting("INIT", step)
                    else:
                        msg = ""
                        if verify["status"] == -1:
                            msg = "远程连接错误!请检查Token或分支是否正确"
                        else:
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
                        context["PROVIDER"] = json.dumps(provider)
                        # Get Provider Settings
                        all_provider = all_providers()
                        context["all_providers"] = dict()
                        for provider in all_provider:
                            params = get_params(provider)
                            context["all_providers"][provider] = params
                        context["all_platform_configs"] = platform_configs()
                else:
                    del provider["params"]["_force"]
                    save_setting("PROVIDER", json.dumps(provider))
                    update_provider()
                    step = "5" if check_if_vercel() else "6"
                    save_setting("INIT", step)
            except Exception as e:
                msg = repr(e)
                logging.error("初始化Provider错误:" + repr(e))
                context["PROVIDER"] = json.dumps(get_setting("PROVIDER") if not provider else provider)
                # Get Provider Settings
                all_provider = all_providers()
                context["all_providers"] = dict()
                for provider in all_provider:
                    params = get_params(provider)
                    context["all_providers"][provider] = params
                context["all_platform_configs"] = platform_configs()
        if request.POST.get("step") == "5":
            project_id = request.POST.get("id")
            vercel_token = request.POST.get("token")
            try:
                checkBuilding(project_id, vercel_token)
                save_setting("VERCEL_TOKEN", vercel_token)
                save_setting("PROJECT_ID", project_id)
                save_setting("INIT", "6")
                step = "6"
            except Exception as e:
                logging.error("初始化Vercel配置错误:" + repr(e))
                context["project_id"] = project_id
                context["vercel_token"] = vercel_token
                msg = "校验错误"
        if step == "6":
            user = User.objects.all()[0]
            context["username"] = user.username
    elif int(step) >= 6:
        logging.info("已完成初始化, 转跳至首页")
        return redirect("/")
    else:
        if int(step) == 3:
            context["PROVIDER"] = get_setting("PROVIDER")
            # Get Provider Settings
            all_provider = all_providers()
            context["all_providers"] = dict()
            for provider in all_provider:
                params = get_params(provider)
                context["all_providers"][provider] = params
            context["all_platform_configs"] = platform_configs()
    context["msg"] = msg
    context["step"] = step
    return render(request, "accounts/init.html", context)


def logout_view(request):
    logout(request)
    logging.info("注销成功")
    return redirect('/login/?next=/')


@login_required(login_url='/login/')
def migrate_view(request):
    if not request.user.is_staff:
        logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
        return page_403(request, "您没有权限访问此页面")
    try:
        if int(get_setting("INIT")) <= 5:
            return redirect("/init/")
    except Exception:
        logging.info("未检测到初始化配置, 转跳到初始化页面")
        return redirect("/init/")
    context = {}
    if request.method == "POST":
        try:
            if request.POST.get("type") == "export":
                exports = dict()
                exports["settings"] = export_settings()
                exports["images"] = export_images()
                exports["friends"] = export_friends()
                exports["notifications"] = export_notifications()
                exports["custom"] = export_customs()
                exports["uv"] = export_uv()
                exports["pv"] = export_pv()
                exports["talks"] = export_talks()
                exports["posts"] = export_posts()
                html_template = loader.get_template('layouts/json.html')
                response = HttpResponse(html_template.render({"data": json.dumps(exports)}, request))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="qexo-export.json"'
                return response
            elif request.POST.get("type") == "import_settings":
                import_settings(json.loads(request.POST.get("data")))
                context["msg"] = "配置迁移完成！"
            elif request.POST.get("type") == "import_images":
                import_images(json.loads(request.POST.get("data")))
                context["msg"] = "图片迁移完成！"
            elif request.POST.get("type") == "import_friends":
                import_friends(json.loads(request.POST.get("data")))
                context["msg"] = "友链迁移完成！"
            elif request.POST.get("type") == "import_notifications":
                import_notifications(json.loads(request.POST.get("data")))
                context["msg"] = "通知迁移完成！"
            elif request.POST.get("type") == "import_custom":
                import_custom(json.loads(request.POST.get("data")))
                context["msg"] = "自定义字段迁移完成！"
            elif request.POST.get("type") == "import_uv":
                import_uv(json.loads(request.POST.get("data")))
                context["msg"] = "UV统计迁移完成！"
            elif request.POST.get("type") == "import_pv":
                import_pv(json.loads(request.POST.get("data")))
                context["msg"] = "PV统计迁移完成！"
            elif request.POST.get("type") == "import_talks":
                import_talks(json.loads(request.POST.get("data")))
                context["msg"] = "说说迁移完成！"
            elif request.POST.get("type") == "import_posts":
                import_posts(json.loads(request.POST.get("data")))
                context["msg"] = "文章索引迁移完成！"
        except Exception as error:
            logging.error(request.POST.get("type") + "错误: " + repr(error))
            context["msg"] = request.POST.get("type") + "错误: " + repr(error)
        return JsonResponse(safe=False, data=context)
    else:
        context = get_custom_config()
    return render(request, "accounts/migrate.html", context)


# Pages
@login_required(login_url="/login/")
def index(request):
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info("初始化未完成, 转跳到初始化页面")
            return redirect("/init/")
    except Exception:
        logging.info("未检测到初始化配置, 转跳到初始化页面")
        return redirect("/init/")
    try:
        if get_setting("JUMP_UPDATE") != "false":
            logging.info("检测到更新配置, 转跳至配置更新页面")
            return redirect("/update/")
    except Exception:
        logging.info("检测配置更新失败, 转跳至更新页面")
        return redirect("/update/")
    context = {'segment': 'index'}
    context.update(get_custom_config())
    cache = Cache.objects.filter(name="posts")
    if cache.count():
        posts = json.loads(cache.first().content)
    else:
        posts = update_posts_cache()
    _images = ImageModel.objects.all().order_by("-date")
    images = list()
    for i in _images:
        images.append({
            "name": i.name,
            "size": convert_to_kb_mb_gb(int(i.size)),
            "url": i.url,
            "date": strftime("%Y-%m-%d", localtime(float(i.date)))
        })
    for item in range(len(posts)):
        posts[item]["quotename"] = quote(posts[item]["name"])
        posts[item]["path"] = quote(posts[item]["path"])
        posts[item]["status"] = "已发布" if posts[item]["status"] else "草稿"
    context["posts"] = json.dumps(posts)
    context["images"] = images
    context = dict(context, **get_latest_version())
    context["version"] = QEXO_VERSION
    context["post_number"] = str(len(posts))
    context["images_number"] = str(len(images))
    context["breadcrumb"] = "Dashboard"
    context["breadcrumb_cn"] = "控制台"
    _recent_posts = PostModel.objects.all().order_by("-date")
    context["recent_posts"] = list()
    for i in _recent_posts:
        context["recent_posts"].append({
            "title": i.title,
            "path": escape(i.path),
            "date": i.date,
            "status": "已发布" if i.status == 1 else "草稿",
            "filename": escape(i.filename)
        })
    save_setting("LAST_LOGIN", str(int(time())))
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = dict()
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info("初始化未完成, 转跳到初始化页面")
            return redirect("/init/")
    except Exception:
        logging.info("未检测到初始化配置, 转跳到初始化页面")
        return redirect("/init/")
    try:
        if get_setting("JUMP_UPDATE") != "false":
            logging.info("检测到更新配置, 转跳至配置更新页面")
            return redirect("/update/")
    except Exception:
        logging.info("检测配置更新失败, 转跳至更新页面")
        return redirect("/update/")
    try:
        context.update(get_custom_config())
        load_template = request.path.split('/')[-1]
        context['segment'] = load_template
        if "index" in load_template:
            return index(request)
        elif "edit_talk" in load_template:
            context["breadcrumb"] = "TalkEditor"
            context["breadcrumb_cn"] = "编辑说说"
            talk_id = request.GET.get("id")
            context["content"] = repr("")
            context["tags"] = "[]"
            context["values"] = "{}"
            context["sidebar"] = get_setting("TALK_SIDEBAR")
            if talk_id:
                Talk = TalkModel.objects.get(id=uuid.UUID(hex=talk_id))
                context["content"] = repr(Talk.content)
                context["tags"] = Talk.tags
                context["id"] = talk_id
                context["values"] = Talk.values
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except Exception:
                logging.info("未检测到图床配置, 图床功能关闭")
        elif "edit_page" in load_template:
            context["breadcrumb"] = "PageEditor"
            file_path = request.GET.get("file")
            context["front_matter"], context["file_content"] = get_post_details(
                (Provider().get_content(file_path)))
            context["front_matter"] = json.dumps(context["front_matter"])
            context['filename'] = file_path.split("/")[-1]
            context["file_path"] = file_path
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("PAGE_SIDEBAR")
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except Exception:
                logging.info("未检测到图床配置, 图床功能关闭")
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
            context["breadcrumb_cn"] = "编辑页面: " + context['filename']
        elif "edit_config" in load_template:
            context["breadcrumb"] = "ConfigEditor"
            file_path = request.GET.get("file")
            context["file_content"] = repr(Provider().get_content(file_path)).replace("<", "\\<").replace(">", "\\>").replace("!", "\\!")
            context["filepath"] = file_path
            context['filename'] = file_path.split("/")[-1]
            context["breadcrumb_cn"] = "编辑配置: " + context['filename']
        elif "edit" in load_template:
            context["breadcrumb"] = "PostEditor"
            file_path = request.GET.get("file")
            context["front_matter"], context["file_content"] = get_post_details(
                (Provider().get_content(file_path)))
            context["front_matter"] = json.dumps(context["front_matter"])
            context['filename'] = request.GET.get("postname")
            context["breadcrumb_cn"] = "编辑文章: " + context['filename']
            context['fullname'] = file_path
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("POST_SIDEBAR")
            context["config"] = Provider().config
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except Exception:
                logging.info("未检测到图床配置, 图床功能关闭")
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
        elif "new_page" in load_template:
            context["breadcrumb"] = "NewPage"
            context["breadcrumb_cn"] = "新建页面"
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("PAGE_SIDEBAR")
            try:
                context["front_matter"], context["file_content"] = get_post_details(
                    (Provider().get_scaffold("pages")))
                context["front_matter"] = json.dumps(context["front_matter"])
            except Exception as error:
                logging.error("获取页面模板失败, 错误信息: " + repr(error))
                # context["error"] = repr(error)
                context["front_matter"], context["file_content"] = {}, ""
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except Exception:
                logging.info("未检测到图床配置, 图床功能关闭")
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
        elif "new" in load_template:
            context["breadcrumb"] = "NewPost"
            context["breadcrumb_cn"] = "新建文章"
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("POST_SIDEBAR")
            context["config"] = Provider().config
            try:
                context["front_matter"], context["file_content"] = get_post_details(
                    (Provider().get_scaffold("posts")))
                context["front_matter"] = json.dumps(context["front_matter"])
            except Exception as error:
                logging.error("获取文章模板失败, 错误信息: " + repr(error))
                # context["error"] = repr(error)
                context["front_matter"], context["file_content"] = {}, ""
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except Exception:
                print("未检测到图床配置, 图床功能关闭")
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
        elif "posts" in load_template:
            context["breadcrumb"] = "Posts"
            context["breadcrumb_cn"] = "文章列表"
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
            for item in range(len(posts)):
                posts[item]["size"] = convert_to_kb_mb_gb(posts[item]["size"])
            context["all_posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "pages" in load_template:
            context["breadcrumb"] = "Pages"
            context["breadcrumb_cn"] = "页面列表"
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
            for item in range(len(posts)):
                posts[item]["size"] = convert_to_kb_mb_gb(posts[item]["size"])
            context["posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "configs" in load_template:
            context["breadcrumb"] = "Configs"
            context["breadcrumb_cn"] = "配置列表"
            if not request.user.is_staff:
                logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
                return page_403(request, "您没有权限访问此页面")
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
            for item in range(len(posts)):
                posts[item]["size"] = convert_to_kb_mb_gb(posts[item]["size"])
            context["posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "talks" in load_template:
            context["breadcrumb"] = "Talks"
            context["breadcrumb_cn"] = "说说列表"
            search = request.GET.get("s")
            posts = []
            talks = TalkModel.objects.all()
            for i in talks:
                t = json.loads(i.like)
                if not search:
                    posts.append({"content": excerpt_post(i.content, 20, mark=False),
                                  "tags": ', '.join(json.loads(i.tags)),
                                  "time": strftime("%Y-%m-%d %H:%M:%S", localtime(int(i.time))),
                                  "like": len(t) if t else 0,
                                  "id": i.id.hex})
                else:
                    if search.upper() in i.content.upper() or search in i.tags.upper() or search in i.values.upper():
                        posts.append({"content": excerpt_post(i.content, 20, mark=False),
                                      "tags": ', '.join(json.loads(i.tags)),
                                      "time": strftime("%Y-%m-%d %H:%M:%S", localtime(int(i.time))),
                                      "like": len(t) if t else 0,
                                      "id": i.id.hex})
            context["posts"] = json.dumps(sorted(posts, key=lambda x: x["time"], reverse=True))
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "images" in load_template:
            context["breadcrumb"] = "Gallery"
            context["breadcrumb_cn"] = "图片列表"
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
            context["posts"] = json.dumps(posts[::-1])
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "friends" in load_template:
            context["breadcrumb"] = "Friends"
            context["breadcrumb_cn"] = "友情链接"
            search = request.GET.get("s")
            posts = []
            images = FriendModel.objects.all()
            for i in images:
                if not search:
                    posts.append({"name": escapeString(i.name), "url": escapeString(i.url), "image": escapeString(i.imageUrl),
                                  "description": escapeString(i.description),
                                  "time": i.time,
                                  "status": i.status})
                else:
                    if search.upper() in i.name.upper() or search.upper() in i.url.upper() or search.upper() in i.description.upper():
                        posts.append({"name": escapeString(i.name), "url": escapeString(i.url), "image": escapeString(i.imageUrl),
                                      "description": escapeString(i.description),
                                      "time": i.time,
                                      "status": i.status})
            posts.sort(key=lambda x: x["time"])
            context["posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif 'settings' in load_template:
            context["breadcrumb"] = "Settings"
            context["breadcrumb_cn"] = "设置"
            if not request.user.is_staff:
                logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
                return page_403(request, "您没有权限访问此页面")
            try:
                context['ABBRLINK_ALG'] = get_setting("ABBRLINK_ALG")
                context['ABBRLINK_REP'] = get_setting("ABBRLINK_REP")
                context["ALLOW_FRIEND"] = get_setting("ALLOW_FRIEND")
                context["STATISTIC_DOMAINS"] = get_setting("STATISTIC_DOMAINS")
                context["STATISTIC_ALLOW"] = get_setting("STATISTIC_ALLOW")
                context["FRIEND_RECAPTCHA"] = get_setting("FRIEND_RECAPTCHA")
                context["RECAPTCHA_TOKEN"] = get_setting("RECAPTCHA_TOKEN")
                context["LOGIN_RECAPTCHA_SITE_TOKEN"] = get_setting("LOGIN_RECAPTCHA_SITE_TOKEN")
                context["LOGIN_RECAPTCHA_SERVER_TOKEN"] = get_setting("LOGIN_RECAPTCHA_SERVER_TOKEN")
                context["LOGIN_RECAPTCHAV2_SITE_TOKEN"] = get_setting("LOGIN_RECAPTCHAV2_SITE_TOKEN")
                context["LOGIN_RECAPTCHAV2_SERVER_TOKEN"] = get_setting("LOGIN_RECAPTCHAV2_SERVER_TOKEN")
                # Get Provider Settings
                context["PROVIDER"] = get_setting("PROVIDER")
                all_provider = all_providers()
                context["all_providers"] = dict()
                for provider in all_provider:
                    params = get_params(provider)
                    context["all_providers"][provider] = params
                # Get OnePush Settings
                context["ONEPUSH"] = get_setting("ONEPUSH")
                all_pusher = onepush_providers()
                context["all_pushers"] = dict()
                for pusher in all_pusher:
                    params = get_notifier(pusher).params
                    if "content" in params["optional"]:
                        params["optional"].remove("content")
                    if "title" in params["optional"]:
                        params["optional"].remove("title")
                    if "content" in params["required"]:
                        params["required"].remove("content")
                    if "title" in params["required"]:
                        params["required"].remove("title")
                    if "mdFormat" not in params["optional"]:
                        params["optional"].append("mdFormat")
                    context["all_pushers"][pusher] = params
                # GET Image Host Settings
                context["IMG_HOST"] = get_setting("IMG_HOST")
                all_provider = all_image_providers()
                context["all_image_hosts"] = dict()
                for provider in all_provider:
                    params = get_image_params(provider)
                    context["all_image_hosts"][provider] = params
                # CDNs
                context["ALL_CDN"] = json.loads(get_setting("ALL_CDN_PREV"))
                # 更新通道
                context["ALL_UPDATES"] = json.loads(get_setting("ALL_UPDATES"))
                context["ALL_PLATFORM_CONFIGS"] = platform_configs()
                context["NOW_PLATFORM_CONFIG"] = Provider().config["name"]
                # Get Auto Excerpt Settings
                context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
                context["AUTO_EXCERPT_SAVE_KEY"] = json.loads(context["AUTO_EXCERPT_CONFIG"]).get("save_key", "excerpt")
                context["AUTO_EXCERPT"] = json.loads(context["AUTO_EXCERPT_CONFIG"]).get("auto", "关闭")
            except Exception:
                logging.error("配置获取错误, 转跳至配置更新页面")
                return redirect("/update/")
        elif 'advanced' in load_template:
            context["breadcrumb"] = "Advanced"
            context["breadcrumb_cn"] = "高级设置"
            if not request.user.is_staff:
                logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
                return page_403(request, "您没有权限访问此页面")
            try:
                search = request.GET.get("s")
                if search:
                    all_settings = SettingModel.objects.filter(name__contains=search.upper())
                    context["search"] = search
                else:
                    all_settings = SettingModel.objects.all()
                context["settings"] = list()
                for setting in all_settings:
                    context["settings"].append({"name": setting.name, "content": setting.content})
                context["settings"].sort(key=lambda elem: elem["name"])  # 按字段名升序排序
                context["settings_number"] = len(context["settings"])
                context["page_number"] = ceil(context["settings_number"] / 15)
            except Exception as e:
                logging.error("高级设置获取错误: " + repr(e))
                context["error"] = repr(e)
        elif 'custom' in load_template:
            context["breadcrumb"] = "Custom"
            context["breadcrumb_cn"] = "自定义字段"
            if not request.user.is_staff:
                logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
                return page_403(request, "您没有权限访问此页面")
            try:
                search = request.GET.get("s")
                all_values = CustomModel.objects.all()
                context["settings"] = list()
                for setting in all_values:
                    if (not search) or (search in setting.name) or (search in setting.content):
                        context["settings"].append({"name": setting.name, "content": setting.content})
                if search:
                    context["search"] = search
                context["settings"].sort(key=lambda elem: elem["name"])  # 按字段名升序排序
                context["settings_number"] = len(context["settings"])
                context["page_number"] = ceil(context["settings_number"] / 15)
            except Exception as e:
                logging.error("自定义字段获取错误: " + repr(e))
                context["error"] = repr(e)
        elif "userscripts" in load_template:
            context["breadcrumb"] = "Scripts"
            context["breadcrumb_cn"] = "在线函数库"
            if not request.user.is_staff:
                logging.info(f"子用户{request.user.username}尝试访问{request.path}被拒绝")
                return page_403(request, "您没有权限访问此页面")
            try:
                search = request.GET.get("s")
                scripts = requests.get("https://raw.githubusercontent.com/Qexo/Scripts/main/index.json").json()
                context["posts"] = list()
                for script in scripts:
                    if (not search) or (search.upper() in script["name"].upper()) or (search.upper() in script["author"].upper()):
                        context["posts"].append(script)
                if search:
                    context["search"] = search
                context["post_number"] = len(context["posts"])
                context["page_number"] = ceil(context["post_number"] / 15)
                context["all_posts"] = json.dumps(context["posts"])
                context["posts"] = json.dumps(context["posts"])
            except Exception as e:
                logging.error("获取错误: " + repr(e))
                context["error"] = repr(e)

        save_setting("LAST_LOGIN", str(int(time())))
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist as e:
        logging.error("页面不存在: " + repr(e))
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as error:
        logging.error("服务端错误: " + repr(error))
        html_template = loader.get_template('home/page-500.html')
        context["error"] = error
        return HttpResponse(html_template.render(context, request))
