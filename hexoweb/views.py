# -*- encoding: utf-8 -*-
import uuid
from math import ceil
from urllib.parse import quote, unquote

from django import template
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader

import hexoweb.libs.i18n
from hexoweb.libs.image import all_providers as all_image_providers
from hexoweb.libs.image import get_params as get_image_params
from hexoweb.libs.onepush import all_providers as onepush_providers
from hexoweb.libs.onepush import get_notifier
from hexoweb.libs.platforms import all_providers, get_params
from hexoweb.libs.platforms import all_configs as platform_configs
from .api import *


def page_404(request, exception):
    return render(request, 'home/page-404.html', {"cdn_prev": "https://unpkg.com/",
                                                  "static_version": QEXO_STATIC})


def page_403(request, exception):
    return render(request, 'home/page-403.html', {"cdn_prev": "https://unpkg.com/",
                                                  "static_version": QEXO_STATIC})


def page_500(request):
    try:
        return render(request, 'home/page-500.html',
                      {"error": gettext("SYSTEM_ERROR"), "cdn_prev": "https://unpkg.com/", "static_version": QEXO_STATIC})
    except Exception as e:
        return render(request, 'home/page-500.html',
                      {"error": repr(e), "cdn_prev": "https://unpkg.com/", "static_version": QEXO_STATIC})


def login_view(request):
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info(gettext("NOT_INIT"))
            return redirect("/init/")
    except Exception:
        logging.info(gettext("NOT_INIT"))
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
        logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
        return page_403(request, gettext("NO_PERMISSION"))
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info(gettext("NOT_INIT"))
            return redirect("/init/")
    except Exception:
        logging.info(gettext("NOT_INIT"))
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
                    context["msg"] = gettext("AUTO_PROVIDER_FAILED")

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
    context = dict(all_languages=hexoweb.libs.i18n.all_languages())
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
            save_setting("LANGUAGE", request.POST.get("language"))
            update_language()
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
                    msg = gettext("RESET_PASSWORD_NO_MATCH")
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                    context["apikey"] = apikey
                elif not password:
                    msg = gettext("RESET_PASSWORD_NO")
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                    context["apikey"] = apikey
                elif not username:
                    msg = gettext("RESET_PASSWORD_NO_USERNAME")
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
                logging.error(gettext("INIT_USER_FAILED").foramt(repr(e)))
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
                                msg += gettext("HEXO_VERSION").format(verify["hexo"])
                            else:
                                msg += gettext("HEXO_VERSION_FAILED")
                            if verify["indexhtml"]:
                                msg += gettext("HEXO_INDEX_FAILED")
                            if verify["config_hexo"]:
                                msg += gettext("HEXO_CONFIG_FAILED")
                            else:
                                msg += gettext("HEXO_CONFIG_FAILED")
                            if verify["theme_dir"]:
                                msg += gettext("HEXO_THEME")
                            else:
                                msg += gettext("HEXO_THEME_FAILED")
                            if verify["package"]:
                                msg += gettext("HEXO_PACKAGE")
                            else:
                                msg += gettext("HEXO_PACKAGE_FAILED")
                            if verify["source"]:
                                msg += gettext("HEXO_SOURCE")
                            else:
                                msg += gettext("HEXO_SOURCE_FAILED")
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
                logging.error(gettext("INIT_PROVIDER_FAILED").format(repr(e)))
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
                logging.error(gettext("INIT_VERCEL_FAILED").format(repr(e)))
                context["project_id"] = project_id
                context["vercel_token"] = vercel_token
                msg = gettext("VERIFY_FAILED")
        if step == "6":
            user = User.objects.all()[0]
            context["username"] = user.username
    elif int(step) >= 6:
        logging.info(gettext("INIT_SUCCESS"))
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
    logging.info(gettext("LOGOUT_SUCCESS"))
    return redirect('/login/?next=/')


@login_required(login_url='/login/')
def migrate_view(request):
    if not request.user.is_staff:
        logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
        return page_403(request, gettext("NO_PERMISSION"))
    try:
        if int(get_setting("INIT")) <= 5:
            return redirect("/init/")
    except Exception:
        logging.info(gettext("NOT_INIT"))
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
                context["msg"] = gettext("MIGRATE_CONFIG_SUCCESS")
            elif request.POST.get("type") == "import_images":
                import_images(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_IMAGE_SUCCESS")
            elif request.POST.get("type") == "import_friends":
                import_friends(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_FLINKS_SUCCESS")
            elif request.POST.get("type") == "import_notifications":
                import_notifications(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_MSG_SUCCESS")
            elif request.POST.get("type") == "import_custom":
                import_custom(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_CUSTOM_SUCCESS")
            elif request.POST.get("type") == "import_uv":
                import_uv(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_UV_SUCCESS")
            elif request.POST.get("type") == "import_pv":
                import_pv(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_PV_SUCCESS")
            elif request.POST.get("type") == "import_talks":
                import_talks(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_TALKS_SUCCESS")
            elif request.POST.get("type") == "import_posts":
                import_posts(json.loads(request.POST.get("data")))
                context["msg"] = gettext("MIGRATE_POST_SUCCESS")
        except Exception as error:
            logging.error(gettext("MIGRATE_FAILED").format(request.POST.get("type"), repr(error)))
            context["msg"] = gettext("MIGRATE_FAILED").format(request.POST.get("type"), repr(error))
        return JsonResponse(safe=False, data=context)
    else:
        context = get_custom_config()
    return render(request, "accounts/migrate.html", context)


# Pages
@login_required(login_url="/login/")
def index(request):
    try:
        if int(get_setting("INIT")) <= 5:
            logging.info(gettext("NOT_INIT"))
            return redirect("/init/")
    except Exception:
        logging.info(gettext("NOT_INIT"))
        return redirect("/init/")
    try:
        if get_setting("JUMP_UPDATE") != "false":
            logging.info(gettext("JUMP_UPDATE"))
            return redirect("/update/")
    except Exception:
        logging.info(gettext("JUMP_UPDATE_FAILED"))
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
        posts[item]["status"] = gettext("PUBLISHED") if posts[item]["status"] else gettext("DRAFT")
    context["posts"] = json.dumps(posts)
    context["images"] = images
    context = dict(context, **get_latest_version())
    context["version"] = QEXO_VERSION
    context["static_version"] = QEXO_STATIC
    context["post_number"] = str(len(posts))
    context["images_number"] = str(len(images))
    context["breadcrumb"] = "Dashboard"
    context["breadcrumb_cn"] = gettext("DASHBOARD")
    _recent_posts = PostModel.objects.all().order_by("-date")
    context["recent_posts"] = list()
    for i in _recent_posts:
        context["recent_posts"].append({
            "title": i.title,
            "path": escape(i.path),
            "date": i.date,
            "status": gettext("PUBLISHED") if i.status == 1 else gettext("DRAFT"),
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
            logging.info(gettext("NOT_INIT"))
            return redirect("/init/")
    except Exception:
        logging.info(gettext("NOT_INIT"))
        return redirect("/init/")
    try:
        if get_setting("JUMP_UPDATE") != "false":
            logging.info(gettext("JUMP_UPDATE"))
            return redirect("/update/")
    except Exception:
        logging.info(gettext("JUMP_UPDATE_FAILED"))
        return redirect("/update/")
    try:
        context.update(get_custom_config())
        load_template = request.path.split('/')[-1]
        context['segment'] = load_template
        if "index" in load_template:
            return index(request)
        elif "edit_talk" in load_template:
            context["breadcrumb"] = "TalkEditor"
            context["breadcrumb_cn"] = gettext("EDIT_TALK")
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
            if json.loads(get_setting("IMG_HOST")).get("type") in hexoweb.libs.image.all_providers():
                context["img_bed"] = True
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
            if json.loads(get_setting("IMG_HOST")).get("type") in hexoweb.libs.image.all_providers():
                context["img_bed"] = True
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
            context["breadcrumb_cn"] = gettext("EDIT_PAGE") + ": " + context['filename']
        elif "edit_config" in load_template:
            context["breadcrumb"] = "ConfigEditor"
            file_path = request.GET.get("file")
            context["file_content"] = repr(Provider().get_content(file_path)).replace("<", "\\<").replace(">", "\\>").replace("!", "\\!")
            context["filepath"] = file_path
            context['filename'] = file_path.split("/")[-1]
            context["breadcrumb_cn"] = gettext("EDIT_CONFIG") + ": " + context['filename']
        elif "edit" in load_template:
            context["breadcrumb"] = "PostEditor"
            file_path = request.GET.get("file")
            context["front_matter"], context["file_content"] = get_post_details(
                (Provider().get_content(file_path)))
            context["front_matter"] = json.dumps(context["front_matter"])
            context['filename'] = request.GET.get("postname")
            context["breadcrumb_cn"] = gettext("EDIT_POST") + ": " + context['filename']
            context['fullname'] = file_path
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("POST_SIDEBAR")
            context["config"] = Provider().config
            if json.loads(get_setting("IMG_HOST")).get("type") in hexoweb.libs.image.all_providers():
                context["img_bed"] = True
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
        elif "new_page" in load_template:
            context["breadcrumb"] = "NewPage"
            context["breadcrumb_cn"] = gettext("NEW_PAGE")
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("PAGE_SIDEBAR")
            try:
                context["front_matter"], context["file_content"] = get_post_details(
                    (Provider().get_scaffold("pages")))
                context["front_matter"] = json.dumps(context["front_matter"])
            except Exception as error:
                logging.error(gettext("GET_PAGE_SCAFFOLD_FAILED").format(repr(error)))
                # context["error"] = repr(error)
                context["front_matter"], context["file_content"] = {}, ""
            if json.loads(get_setting("IMG_HOST")).get("type") in hexoweb.libs.image.all_providers():
                context["img_bed"] = True
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
        elif "new" in load_template:
            context["breadcrumb"] = "NewPost"
            context["breadcrumb_cn"] = gettext("NEW_POST")
            context["emoji"] = get_setting("VDITOR_EMOJI")
            context["sidebar"] = get_setting("POST_SIDEBAR")
            context["config"] = Provider().config
            try:
                context["front_matter"], context["file_content"] = get_post_details(
                    (Provider().get_scaffold("posts")))
                context["front_matter"] = json.dumps(context["front_matter"])
            except Exception as error:
                logging.error(gettext("GET_POST_SCAFFOLD_FAILED").format(repr(error)))
                # context["error"] = repr(error)
                context["front_matter"], context["file_content"] = {}, ""
            if json.loads(get_setting("IMG_HOST")).get("type") in hexoweb.libs.image.all_providers():
                context["img_bed"] = True
            context["AUTO_EXCERPT_CONFIG"] = get_setting("AUTO_EXCERPT_CONFIG")
        elif "posts" in load_template:
            context["breadcrumb"] = "Posts"
            context["breadcrumb_cn"] = gettext("POSTS_LIST")
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
            context["new_dir"] = Provider().config["posts"]["save_path"]
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "pages" in load_template:
            context["breadcrumb"] = "Pages"
            context["breadcrumb_cn"] = gettext("PAGES_LIST")
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
            context["new_dir"] = Provider().config["pages"]["save_path"]
            context["posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "configs" in load_template:
            context["breadcrumb"] = "Configs"
            context["breadcrumb_cn"] = gettext("CONFIGS_LIST")
            if not request.user.is_staff:
                logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
                return page_403(request, gettext("NO_PERMISSION"))
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
            context["breadcrumb_cn"] = gettext("TALKS_LIST")
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
            context["breadcrumb_cn"] = gettext("IMAGES_LIST")
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
            context["breadcrumb_cn"] = gettext("FLINKS_LIST")
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
            context["breadcrumb_cn"] = gettext("SETTINGS")
            if not request.user.is_staff:
                logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
                return page_403(request, gettext("NO_PERMISSION"))
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
                logging.error(gettext("GET_SETTINGS_FAILED"))
                return redirect("/update/")
        elif 'advanced' in load_template:
            context["breadcrumb"] = "Advanced"
            context["breadcrumb_cn"] = gettext("ADVANCED_SETTINGS")
            if not request.user.is_staff:
                logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
                return page_403(request, gettext("NO_PERMISSION"))
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
                logging.error(gettext("GET_ADVANCED_SETTINGS_FAILED").format(repr(e)))
                context["error"] = repr(e)
        elif 'custom' in load_template:
            context["breadcrumb"] = "Custom"
            context["breadcrumb_cn"] = gettext("CUSTOM_LIST")
            if not request.user.is_staff:
                logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
                return page_403(request, gettext("NO_PERMISSION"))
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
                logging.error(gettext("GET_CUSTOM_FAILED").format(repr(e)))
                context["error"] = repr(e)
        elif "userscripts" in load_template:
            context["breadcrumb"] = "Scripts"
            context["breadcrumb_cn"] = gettext("SCRIPTS_LIST")
            if not request.user.is_staff:
                logging.info(gettext("USER_IS_NOT_STAFF").format(request.user.username, request.path))
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
                logging.error(gettext("GET_SCRIPTS_FAILED").format(repr(e)))
                context["error"] = repr(e)

        save_setting("LAST_LOGIN", str(int(time())))
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist as e:
        logging.error(gettext("PAGE_404").format(repr(e)))
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as error:
        logging.error(gettext("PAGE_500").format(repr(e)))
        html_template = loader.get_template('home/page-500.html')
        context["error"] = error
        return HttpResponse(html_template.render(context, request))
