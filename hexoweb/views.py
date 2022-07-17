# -*- encoding: utf-8 -*-
from django.shortcuts import redirect
from django.contrib.auth import logout
from django import template
from django.http import HttpResponse
from django.template import loader
from .api import *
from math import ceil


def page_404(request, exception):
    return render(request, 'home/page-404.html', {"cdn_prev": "https://unpkg.com/", "cdnjs": "https://cdn.staticfile.org/"})


def page_403(request, exception):
    return render(request, 'home/page-403.html', {"cdn_prev": "https://unpkg.com/", "cdnjs": "https://cdn.staticfile.org/"})


def page_500(request):
    return render(request, 'home/page-500.html',
                  {"error": "程序遇到了错误！", "cdn_prev": "https://unpkg.com/", "cdnjs": "https://cdn.staticfile.org/"})


def login_view(request):
    try:
        if int(get_setting("INIT")) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
    if request.user.is_authenticated:
        if not request.GET.get("next"):
            return redirect("/")
        else:
            return redirect(request.GET.get("next"))
    context = get_custom_config()
    site_token = get_setting("LOGIN_RECAPTCHA_SITE_TOKEN")
    server_token = get_setting("LOGIN_RECAPTCHA_SERVER_TOKEN")
    if site_token and server_token:
        context["site_token"] = site_token
    return render(request, "accounts/login.html", context)


@login_required(login_url="/login/")
def update_view(request):
    try:
        if int(get_setting("INIT")) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
    if request.method == 'POST':
        for setting in request.POST.keys():
            save_setting(setting, request.POST.get(setting))
            if setting == "PROVIDER":
                update_provider()
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
    delete_all_caches()  # delete all caches
    if not context["counter"]:
        save_setting("UPDATE_FROM", QEXO_VERSION)
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
    if request.method == "POST":
        if request.POST.get("step") == "1":
            fix_all()
            save_setting("INIT", "2")
            step = "2"
        if request.POST.get("step") == "2":
            try:
                apikey = request.POST.get("apikey")
                if apikey:
                    save_setting("WEBHOOK_APIKEY", apikey)
                else:
                    if not SettingModel.objects.filter(name="WEBHOOK_APIKEY").count():
                        save_setting("WEBHOOK_APIKEY", ''.join(
                            random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in
                            range(12)))
                username = request.POST.get("username")
                password = request.POST.get("password")
                repassword = request.POST.get("repassword")
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
            except Exception as e:
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
                del provider["params"]["provider"]
                del provider["params"]["step"]
                del provider["params"]["csrfmiddlewaretoken"]
                for key in provider["params"].keys():
                    provider["params"][key] = provider["params"][key][0]
                verify = verify_provider(provider)
                if verify["status"] and verify["status"] != -1:
                    save_setting("PROVIDER", json.dumps(provider))
                    update_provider()
                    step = "5" if check_if_vercel() else "6"
                    save_setting("INIT", step)
                else:
                    msg = ""
                    if verify["status"] == -1:
                        msg = "远程连接错误!请检查Token"
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
                    context["PROVIDER"] = provider
                    # Get Provider Settings
                    all_provider = all_providers()
                    context["all_providers"] = dict()
                    for provider in all_provider:
                        params = get_params(provider)
                        context["all_providers"][provider] = params
            except Exception as e:
                msg = repr(e)
                context["PROVIDER"] = get_setting("PROVIDER")
                # Get Provider Settings
                all_provider = all_providers()
                context["all_providers"] = dict()
                for provider in all_provider:
                    params = get_params(provider)
                    context["all_providers"][provider] = params
        if request.POST.get("step") == "5":
            project_id = request.POST.get("id")
            vercel_token = request.POST.get("token")
            try:
                checkBuilding(project_id, vercel_token)
                save_setting("VERCEL_TOKEN", vercel_token)
                save_setting("PROJECT_ID", project_id)
                save_setting("INIT", "6")
                step = "6"
            except:
                context["project_id"] = project_id
                context["vercel_token"] = vercel_token
                msg = "校验错误"
        if step == "6":
            user = User.objects.all()[0]
            context["username"] = user.username
    elif int(step) >= 6:
        return redirect("/")
    if int(step) == 3:
        context["PROVIDER"] = get_setting("PROVIDER")
        # Get Provider Settings
        all_provider = all_providers()
        context["all_providers"] = dict()
        for provider in all_provider:
            params = get_params(provider)
            context["all_providers"][provider] = params
    context["msg"] = msg
    context["step"] = step
    return render(request, "accounts/init.html", context)


def logout_view(request):
    logout(request)
    return redirect('/login/?next=/')


# Pages
@login_required(login_url="/login/")
def index(request):
    try:
        if int(get_setting("INIT")) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
    try:
        if get_setting("UPDATE_FROM") != QEXO_VERSION:
            return redirect("/update/")
    except:
        return redirect("/update/")
    context = {'segment': 'index'}
    context.update(get_custom_config())
    cache = Cache.objects.filter(name="posts")
    if cache.count():
        posts = json.loads(cache.first().content)
    else:
        posts = update_posts_cache()
    _images = ImageModel.objects.all()
    images = list()
    for i in _images:
        images.append({"name": i.name, "size": int(i.size), "url": i.url,
                       "date": strftime("%Y-%m-%d", localtime(float(i.date)))})
    if len(posts) >= 5:
        context["posts"] = posts[0:5]
    else:
        context["posts"] = posts
    for item in range(len(context["posts"])):
        context["posts"][item]["fullname"] = quote(context["posts"][item]["fullname"])
    if len(images) >= 5:
        context["images"] = images[::-1][0:5]
    else:
        context["images"] = images[::-1]
    context = dict(context, **get_latest_version())
    context["version"] = QEXO_VERSION
    context["post_number"] = str(len(posts))
    context["images_number"] = str(len(images))
    save_setting("LAST_LOGIN", str(int(time())))
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = dict()
    try:
        if int(get_setting("INIT")) <= 5:
            return redirect("/init/")
    except:
        pass
    try:
        if get_setting("UPDATE_FROM") != QEXO_VERSION:
            return redirect("/update/")
    except:
        return redirect("/update/")
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        context.update(get_custom_config())
        load_template = request.path.split('/')[-1]
        context['segment'] = load_template
        if "index" in load_template:
            return index(request)
        elif "edit_page" in load_template:
            file_path = request.GET.get("file")
            context["front_matter"], context["file_content"] = get_post_details(
                (Provider().get_content(file_path)))
            context["json_front_matter"] = json.dumps(context["front_matter"])
            context['filename'] = file_path.split("/")[-2] + "/" + file_path.split("/")[-1]
            context["file_path"] = file_path
            context["emoji"] = get_setting("VDITOR_EMOJI")
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except:
                pass
        elif "edit_config" in load_template:
            file_path = request.GET.get("file")
            context["file_content"] = repr(Provider().get_content(file_path)).replace("<", "\\<").replace(">", "\\>").replace("!", "\\!")
            context["filepath"] = file_path
            context['filename'] = file_path.split("/")[-1]
        elif "edit" in load_template:
            file_path = request.GET.get("file")
            context["front_matter"], context["file_content"] = get_post_details(
                (get_post(file_path)))
            context["json_front_matter"] = json.dumps(context["front_matter"])
            context['filename'] = file_path.split("/")[-1]
            context['fullname'] = file_path
            context["emoji"] = get_setting("VDITOR_EMOJI")
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except:
                pass
        elif "new_page" in load_template:
            context["emoji"] = get_setting("VDITOR_EMOJI")
            try:
                context["front_matter"], context["file_content"] = get_post_details(
                    (Provider().get_content("scaffolds/page.md")))
                context["json_front_matter"] = json.dumps(context["front_matter"])
            except Exception as error:
                context["error"] = repr(error)
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except:
                pass
        elif "new" in load_template:
            context["emoji"] = get_setting("VDITOR_EMOJI")
            try:
                context["front_matter"], context["file_content"] = get_post_details(
                    (Provider().get_content("scaffolds/post.md")))
                context["json_front_matter"] = json.dumps(context["front_matter"])
            except Exception as error:
                context["error"] = repr(error)
            try:
                if json.loads(get_setting("IMG_HOST"))["type"] != "关闭":
                    context["img_bed"] = True
            except:
                pass
        elif "posts" in load_template:
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
            context["all_posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "pages" in load_template:
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
            context["posts"] = posts
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "configs" in load_template:
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
            context["posts"] = posts
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "images" in load_template:
            search = request.GET.get("s")
            posts = []
            if search:
                images = ImageModel.objects.filter(name__contains=search)
                for i in images:
                    posts.append({"name": i.name, "size": int(i.size), "url": i.url,
                                  "date": strftime("%Y-%m-%d %H:%M:%S",
                                                   localtime(float(i.date))),
                                  "time": i.date})
            else:
                images = ImageModel.objects.all()
                for i in images:
                    posts.append({"name": i.name, "size": int(i.size), "url": i.url,
                                  "date": strftime("%Y-%m-%d %H:%M:%S",
                                                   localtime(float(i.date))),
                                  "time": i.date})
            context["posts"] = posts[::-1]
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif "friends" in load_template:
            search = request.GET.get("s")
            posts = []
            if search:
                friends = FriendModel.objects.filter(name__contains=search)
                for i in friends:
                    posts.append({"name": i.name, "url": i.url, "image": i.imageUrl,
                                  "description": i.description,
                                  "time": i.time,
                                  "status": i.status})
            else:
                images = FriendModel.objects.all()
                for i in images:
                    posts.append({"name": i.name, "url": i.url, "image": i.imageUrl,
                                  "description": i.description,
                                  "time": i.time,
                                  "status": i.status})
            posts.sort(key=lambda x: x["time"])
            context["posts"] = json.dumps(posts)
            context["post_number"] = len(posts)
            context["page_number"] = ceil(context["post_number"] / 15)
            context["search"] = search
        elif 'settings' in load_template:
            try:
                context['GH_REPO_PATH'] = get_setting("GH_REPO_PATH")
                context['GH_REPO_BRANCH'] = get_setting("GH_REPO_BRANCH")
                context['GH_REPO'] = get_setting("GH_REPO")
                context['GH_TOKEN'] = get_setting("GH_TOKEN")
                token_len = len(context['GH_TOKEN'])
                if token_len >= 5:
                    context['GH_TOKEN'] = context['GH_TOKEN'][:3] + "*" * (token_len - 5) + \
                                          context['GH_TOKEN'][-1]
                context['IMG_TYPE'] = get_setting("IMG_TYPE")
                context['ABBRLINK_ALG'] = get_setting("ABBRLINK_ALG")
                context['ABBRLINK_REP'] = get_setting("ABBRLINK_REP")
                context["ALLOW_FRIEND"] = get_setting("ALLOW_FRIEND")
                context["STATISTIC_DOMAINS"] = get_setting("STATISTIC_DOMAINS")
                context["STATISTIC_ALLOW"] = get_setting("STATISTIC_ALLOW")
                context["FRIEND_RECAPTCHA"] = get_setting("FRIEND_RECAPTCHA")
                context["RECAPTCHA_TOKEN"] = get_setting("RECAPTCHA_TOKEN")
                context["LOGIN_RECAPTCHA_SITE_TOKEN"] = get_setting("LOGIN_RECAPTCHA_SITE_TOKEN")
                context["LOGIN_RECAPTCHA_SERVER_TOKEN"] = get_setting("LOGIN_RECAPTCHA_SERVER_TOKEN")
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
                    if "markdown" not in params["optional"]:
                        params["optional"].append("markdown")
                    context["all_pushers"][pusher] = params
                # GET Image Host Settings
                context["IMG_HOST"] = get_setting("IMG_HOST")
                all_provider = all_image_providers()
                context["all_image_hosts"] = dict()
                for provider in all_provider:
                    params = get_image_params(provider)
                    context["all_image_hosts"][provider] = params
            except:
                return redirect("/update/")
        elif 'advanced' in load_template:
            try:
                all_settings = SettingModel.objects.all()
                context["settings"] = list()
                for setting in all_settings:
                    context["settings"].append({"name": setting.name, "content": setting.content})
                context["settings"].sort(key=lambda elem: elem["name"])  # 按字段名升序排序
                context["settings_number"] = len(context["settings"])
                context["page_number"] = ceil(context["settings_number"] / 15)
            except Exception as e:
                context["error"] = repr(e)
        elif 'custom' in load_template:
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
                context["error"] = repr(e)
        save_setting("LAST_LOGIN", str(int(time())))
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as error:
        html_template = loader.get_template('home/page-500.html')
        context["error"] = error
        return HttpResponse(html_template.render(context, request))
