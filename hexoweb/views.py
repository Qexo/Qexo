# -*- encoding: utf-8 -*-
from django.shortcuts import redirect
from django.contrib.auth import logout
from django import template
from django.http import HttpResponse
from django.template import loader
from time import strftime, localtime
from .api import *


def page_404(request, exception):
    return render(request, 'home/page-404.html', {"cdn_prev": "https://cdn.jsdelivr.net/npm/"})


def page_500(request):
    return render(request, 'home/page-500.html',
                  {"error": "程序遇到了错误！", "cdn_prev": "https://cdn.jsdelivr.net/npm/"})


def login_view(request):
    try:
        if int(SettingModel.objects.get(name="INIT").content) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
    if request.user.is_authenticated:
        if not request.GET.get("next"):
            return redirect("/")
        else:
            return redirect(request.GET.get("next"))
    return render(request, "accounts/login.html", get_custom_config())


def init_view(request):
    msg = None
    context = dict()
    context.update(get_custom_config())
    try:
        step = SettingModel.objects.get(name="INIT").content
    except:
        save_setting("INIT", "1")
        step = "1"
    if request.method == "POST":
        if request.POST.get("step") == "1":
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
                repo = request.POST.get("repo")
                branch = request.POST.get("branch")
                token = request.POST.get("token")
                path = request.POST.get("path")
                try:
                    _repo = github.Github(token).get_repo(repo).get_contents(path + "source/_posts",
                                                                             ref=branch)
                    save_setting("GH_REPO_PATH", path)
                    save_setting("GH_REPO_BRANCH", branch)
                    save_setting("GH_REPO", repo)
                    save_setting("GH_TOKEN", token)
                    save_setting("INIT", "4")
                    step = "4"
                except:
                    msg = "校验失败"
                    context["repo"] = repo
                    context["branch"] = branch
                    context["token"] = token
                    context["path"] = path
            except Exception as e:
                msg = repr(e)
                context["repo"] = repo
                context["branch"] = branch
                context["token"] = token
                context["path"] = path
        if request.POST.get("step") == "4":
            api = request.POST.get("api")
            post_params = request.POST.get("post")
            json_path = request.POST.get("jsonpath")
            custom_body = request.POST.get("body")
            custom_header = request.POST.get("header")
            custom_url = request.POST.get("custom")
            try:
                save_setting("IMG_API", api)
                save_setting("IMG_POST", post_params)
                save_setting("IMG_JSON_PATH", json_path)
                save_setting("IMG_CUSTOM_BODY", custom_body)
                save_setting("IMG_CUSTOM_HEADER", custom_header)
                save_setting("IMG_CUSTOM_URL", custom_url)
                save_setting("INIT", "5")
                step = "5"
            except Exception as e:
                msg = repr(e)
                context["api"] = api
                context["post"] = post_params
                context["jsonpath"] = json_path
                context["body"] = custom_body
                context["header"] = custom_header
                context["custom"] = custom_url
        if request.POST.get("step") == "5":
            update_repo = request.POST.get("repo")
            update_token = request.POST.get("token")
            update_branch = request.POST.get("branch")
            origin_branch = request.POST.get("origin")
            if update_branch and update_token and update_repo:
                try:
                    user = github.Github(update_token)
                    user.get_repo(update_repo).get_contents("", ref=update_branch)
                    user.get_repo("am-abudu/Qexo").get_contents("", ref=origin_branch)
                    save_setting("UPDATE_REPO", update_repo)
                    save_setting("UPDATE_TOKEN", update_token)
                    save_setting("UPDATE_REPO_BRANCH", update_branch)
                    save_setting("INIT", "6")
                    step = "6"
                except:
                    msg = "校验失败"
                    context["repo"] = update_repo
                    context["token"] = update_token
                    context["branch"] = update_branch
                    context["origin"] = origin_branch
            else:
                save_setting("UPDATE_REPO", update_repo)
                save_setting("UPDATE_TOKEN", update_token)
                save_setting("UPDATE_REPO_BRANCH", update_branch)
                save_setting("UPDATE_ORIGIN_BRANCH", origin_branch)
                save_setting("INIT", "6")
                step = "6"
        if step == "6":
            user = User.objects.all()[0]
            context["username"] = user.username
    elif int(step) >= 6:
        return redirect("/")
    return render(request, "accounts/init.html", {"msg": msg, "step": step, "context": context})


def logout_view(request):
    logout(request)
    return redirect('/login/?next=/')


# Pages
@login_required(login_url="/login/")
def index(request):
    try:
        if int(SettingModel.objects.get(name="INIT").content) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
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
    if len(images) >= 5:
        context["images"] = images[0:5]
    else:
        context["images"] = images
    context = dict(context, **get_latest_version())
    context["version"] = QEXO_VERSION
    context["post_number"] = str(len(posts))
    context["images_number"] = str(len(images))
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = dict()
    try:
        if int(SettingModel.objects.get(name="INIT").content) <= 5:
            return redirect("/init/")
    except:
        pass
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        context.update(get_custom_config())
        load_template = request.path.split('/')[-1]
        context['segment'] = load_template
        if "index" in load_template:
            return index(request)
        elif "edit_page" in load_template:
            repo = get_repo()
            file_path = request.GET.get("file")
            context["file_content"] = repr(
                repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content + file_path,
                                  ref=SettingModel.objects.get(
                                      name="GH_REPO_BRANCH").content).decoded_content.decode(
                    "utf8")).replace("<",
                                     "\\<").replace(
                ">", "\\>").replace("!", "\\!")
            context['filename'] = file_path.split("/")[-2] + "/" + file_path.split("/")[-1]
            context["file_path"] = file_path
            context["emoji"] = SettingModel.objects.get(name="VDITOR_EMOJI").content
            try:
                if SettingModel.objects.get(
                        name="IMG_TYPE").content:
                    context["img_bed"] = True
            except Exception as error:
                context["error"] = repr(error)
        elif "edit_config" in load_template:
            file_path = request.GET.get("file")
            repo = get_repo()
            context["file_content"] = repr(repo.get_contents(
                SettingModel.objects.get(name="GH_REPO_PATH").content + file_path,
                ref=SettingModel.objects.get(
                    name="GH_REPO_BRANCH").content).decoded_content.decode(
                "utf8")).replace("<", "\\<").replace(">", "\\>").replace("!", "\\!")
            context["filepath"] = file_path
            context['filename'] = file_path.split("/")[-1]
        elif "edit" in load_template:
            file_path = request.GET.get("file")
            context["file_content"] = repr(get_post(file_path)).replace("<",
                                                                        "\\<").replace(
                ">", "\\>").replace("!", "\\!")
            context['filename'] = file_path.split("/")[-1]
            context['fullname'] = file_path
            context["emoji"] = SettingModel.objects.get(name="VDITOR_EMOJI").content
            try:
                if SettingModel.objects.get(
                        name="IMG_TYPE").content:
                    context["img_bed"] = True
            except Exception as error:
                context["error"] = repr(error)
        elif "new_page" in load_template:
            repo = get_repo()
            context["emoji"] = SettingModel.objects.get(name="VDITOR_EMOJI").content
            try:
                now = time()
                alg = SettingModel.objects.get(name="ABBRLINK_ALG").content
                rep = SettingModel.objects.get(name="ABBRLINK_REP").content
                abbrlink = get_crc_by_time(str(now), alg, rep)
                context["file_content"] = repr(
                    repo.get_contents(
                        SettingModel.objects.get(name="GH_REPO_PATH").content + "scaffolds/page.md",
                        ref=SettingModel.objects.get(
                            name="GH_REPO_BRANCH").content).decoded_content.decode("utf8")).replace(
                    "<", "\\<").replace(">", "\\>").replace("{{ date }}",
                                                            strftime("%Y-%m-%d %H:%M:%S",
                                                                     localtime(now))).replace(
                    "{{ abbrlink }}", abbrlink).replace("!", "\\!")
            except Exception as error:
                context["error"] = repr(error)
            try:
                if SettingModel.objects.get(
                        name="IMG_TYPE").content:
                    context["img_bed"] = True
            except Exception as error:
                context["error"] = repr(error)
        elif "new" in load_template:
            repo = get_repo()
            context["emoji"] = SettingModel.objects.get(name="VDITOR_EMOJI").content
            try:
                now = time()
                alg = SettingModel.objects.get(name="ABBRLINK_ALG").content
                rep = SettingModel.objects.get(name="ABBRLINK_REP").content
                abbrlink = get_crc_by_time(str(now), alg, rep)
                context["file_content"] = repr(
                    repo.get_contents(
                        SettingModel.objects.get(name="GH_REPO_PATH").content + "scaffolds/post.md",
                        ref=SettingModel.objects.get(
                            name="GH_REPO_BRANCH").content).decoded_content.decode("utf8").replace(
                        "{{ date }}", strftime("%Y-%m-%d %H:%M:%S", localtime(
                            now))).replace("{{ abbrlink }}", abbrlink)).replace("<",
                                                                                "\\<").replace(
                    ">", "\\>").replace("!", "\\!")

            except Exception as error:
                context["error"] = repr(error)
            try:
                if SettingModel.objects.get(
                        name="IMG_TYPE").content:
                    context["img_bed"] = True
            except Exception as error:
                context["error"] = repr(error)
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
            context["page_number"] = context["post_number"] // 15 + 1
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
            context["page_number"] = context["post_number"] // 15 + 1
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
            context["page_number"] = context["post_number"] // 15 + 1
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
            context["posts"] = posts
            context["post_number"] = len(posts)
            context["page_number"] = context["post_number"] // 15 + 1
            context["search"] = search
        elif 'settings' in load_template:
            try:
                try:
                    context['GH_REPO_PATH'] = SettingModel.objects.get(name="GH_REPO_PATH").content
                except:
                    save_setting('GH_REPO_PATH', '')
                try:
                    context['GH_REPO_BRANCH'] = SettingModel.objects.get(
                        name="GH_REPO_BRANCH").content
                except:
                    save_setting('GH_REPO_BRANCH', '')
                try:
                    context['GH_REPO'] = SettingModel.objects.get(name="GH_REPO").content
                except:
                    save_setting('GH_REPO', '')
                try:
                    context['GH_TOKEN'] = SettingModel.objects.get(name="GH_TOKEN").content
                    token_len = len(context['GH_TOKEN'])
                    if token_len >= 5:
                        context['GH_TOKEN'] = context['GH_TOKEN'][:3] + "*" * (token_len - 5) + \
                                              context['GH_TOKEN'][-1]
                except:
                    save_setting('GH_TOKEN', '')
                try:
                    context['IMG_CUSTOM_URL'] = SettingModel.objects.get(
                        name='IMG_CUSTOM_URL').content
                except:
                    save_setting('IMG_CUSTOM_URL', '')
                try:
                    context['IMG_CUSTOM_HEADER'] = SettingModel.objects.get(
                        name='IMG_CUSTOM_HEADER').content
                except:
                    save_setting('IMG_CUSTOM_HEADER', '')
                try:
                    context['IMG_CUSTOM_BODY'] = SettingModel.objects.get(
                        name='IMG_CUSTOM_BODY').content
                except:
                    save_setting('IMG_CUSTOM_BODY', '')
                try:
                    context['IMG_JSON_PATH'] = SettingModel.objects.get(
                        name='IMG_JSON_PATH').content
                except:
                    save_setting('IMG_JSON_PATH', '')
                try:
                    context['IMG_POST'] = SettingModel.objects.get(name='IMG_POST').content
                except:
                    save_setting('IMG_POST', '')
                try:
                    context['IMG_API'] = SettingModel.objects.get(name='IMG_API').content
                except:
                    save_setting('IMG_API', '')
                try:
                    context['UPDATE_REPO_BRANCH'] = SettingModel.objects.get(
                        name="UPDATE_REPO_BRANCH").content
                except:
                    save_setting('UPDATE_REPO_BRANCH', '')
                try:
                    context['UPDATE_REPO'] = SettingModel.objects.get(name="UPDATE_REPO").content
                except:
                    save_setting('UPDATE_REPO', '')
                try:
                    context['UPDATE_ORIGIN_BRANCH'] = SettingModel.objects.get(
                        name="UPDATE_ORIGIN_BRANCH").content
                except:
                    save_setting('UPDATE_ORIGIN_BRANCH', 'master')
                    context['UPDATE_ORIGIN_BRANCH'] = "master"
                try:
                    context['UPDATE_TOKEN'] = SettingModel.objects.get(name="UPDATE_TOKEN").content
                    if len(context['UPDATE_TOKEN']) >= 5:
                        context['UPDATE_TOKEN'] = context['UPDATE_TOKEN'][:3] + "*" * (
                                token_len - 5) \
                                                  + context['UPDATE_TOKEN'][-1]
                except:
                    save_setting('UPDATE_TOKEN', '')
                if context['UPDATE_REPO_BRANCH'] and context['UPDATE_REPO'] \
                        and context['UPDATE_TOKEN']:
                    context["showUpdate"] = True
                try:
                    context['S3_KEY_ID'] = SettingModel.objects.get(
                        name="S3_KEY_ID").content
                except:
                    save_setting('S3_KEY_ID', '')
                try:
                    context['S3_ACCESS_KEY'] = SettingModel.objects.get(
                        name="S3_ACCESS_KEY").content
                except:
                    save_setting('S3_ACCESS_KEY', '')
                try:
                    context['S3_ENDPOINT'] = SettingModel.objects.get(
                        name="S3_ENDPOINT").content
                except:
                    save_setting('S3_ENDPOINT', '')
                try:
                    context['S3_BUCKET'] = SettingModel.objects.get(
                        name="S3_BUCKET").content
                except:
                    save_setting('S3_BUCKET', '')
                try:
                    context['S3_PATH'] = SettingModel.objects.get(
                        name="S3_PATH").content
                except:
                    save_setting('S3_PATH', '')
                try:
                    context['S3_PREV_URL'] = SettingModel.objects.get(
                        name="S3_PREV_URL").content
                except:
                    save_setting('S3_PREV_URL', '')
                try:
                    context['IMG_TYPE'] = SettingModel.objects.get(
                        name="IMG_TYPE").content
                except:
                    save_setting('IMG_TYPE', '')
                try:
                    context['ABBRLINK_ALG'] = SettingModel.objects.get(
                        name="ABBRLINK_ALG").content
                except:
                    save_setting('ABBRLINK_ALG', 'crc16')
                    context['ABBRLINK_ALG'] = "crc16"
                try:
                    context['ABBRLINK_REP'] = SettingModel.objects.get(
                        name="ABBRLINK_REP").content
                except:
                    save_setting('ABBRLINK_REP', 'dec')
                    context['ABBRLINK_REP'] = "dec"
                try:
                    SettingModel.objects.get(name="VDITOR_EMOJI").content
                except:
                    save_setting('VDITOR_EMOJI',
                                 """{"\u5fae\u7b11":"\ud83d\ude42","\u6487\u5634":"\ud83d\ude26","\u8272":"\ud83d\ude0d","\u53d1\u5446":"\ud83d\ude0d","\u5f97\u610f":"\ud83d\ude0e","\u6d41\u6cea":"\ud83d\ude2d","\u5bb3\u7f9e":"\ud83d\ude0a","\u95ed\u5634":"\ud83d\ude37","\u7761":"\ud83d\ude34","\u5927\u54ed ":"\ud83d\ude21","\u5c34\u5c2c":"\ud83d\ude21","\u53d1\u6012":"\ud83d\ude1b","\u8c03\u76ae":"\ud83d\ude00","\u5472\u7259":"\ud83d\ude2f","\u60ca\u8bb6":"\ud83d\ude41","\u96be\u8fc7":"\ud83d\ude0e","\u9177":"\ud83d\ude28","\u51b7\u6c57":"\ud83d\ude31","\u6293\u72c2":"\ud83d\ude35","\u5410 ":"\ud83d\ude0b","\u5077\u7b11":"\u263a","\u6109\u5feb":"\ud83d\ude44","\u767d\u773c":"\ud83d\ude44","\u50b2\u6162":"\ud83d\ude0b","\u9965\u997f":"\ud83d\ude2a","\u56f0":"\ud83d\ude2b","\u60ca\u6050":"\ud83d\ude13","\u6d41\u6c57":"\ud83d\ude03","\u61a8\u7b11":"\ud83d\ude03","\u60a0\u95f2 ":"\ud83d\ude06","\u594b\u6597":"\ud83d\ude06","\u5492\u9a82":"\ud83d\ude06","\u7591\u95ee":"\ud83d\ude06","\u5618":"\ud83d\ude35","\u6655":"\ud83d\ude06","\u75af\u4e86":"\ud83d\ude06","\u8870":"\ud83d\ude06","\u9ab7\u9ac5":"\ud83d\udc80","\u6572\u6253":"\ud83d\ude2c","\u518d\u89c1 ":"\ud83d\ude18","\u64e6\u6c57":"\ud83d\ude06","\u62a0\u9f3b":"\ud83d\ude06","\u9f13\u638c":"\ud83d\udc4f","\u7cd7\u5927\u4e86":"\ud83d\ude06","\u574f\u7b11":"\ud83d\ude06","\u5de6\u54fc\u54fc":"\ud83d\ude06","\u53f3\u54fc\u54fc":"\ud83d\ude06","\u54c8\u6b20":"\ud83d\ude06","\u9119\u89c6":"\ud83d\ude06","\u59d4\u5c48 ":"\ud83d\ude06","\u5feb\u54ed\u4e86":"\ud83d\ude06","\u9634\u9669":"\ud83d\ude06","\u4eb2\u4eb2":"\ud83d\ude18","\u5413":"\ud83d\ude13","\u53ef\u601c":"\ud83d\ude06","\u83dc\u5200":"\ud83d\udd2a","\u897f\u74dc":"\ud83c\udf49","\u5564\u9152":"\ud83c\udf7a","\u7bee\u7403":"\ud83c\udfc0","\u4e52\u4e53 ":"\u26aa","\u5496\u5561":"\u2615","\u996d":"\ud83c\udf5a","\u732a\u5934":"\ud83d\udc37","\u73ab\u7470":"\ud83c\udf39","\u51cb\u8c22":"\ud83c\udf39","\u5634\u5507":"\ud83d\udc44","\u7231\u5fc3":"\ud83d\udc97","\u5fc3\u788e":"\ud83d\udc94","\u86cb\u7cd5":"\ud83c\udf82","\u95ea\u7535 ":"\u26a1","\u70b8\u5f39":"\ud83d\udca3","\u5200":"\ud83d\udde1","\u8db3\u7403":"\u26bd","\u74e2\u866b":"\ud83d\udc1e","\u4fbf\u4fbf":"\ud83d\udca9","\u6708\u4eae":"\ud83c\udf19","\u592a\u9633":"\u2600","\u793c\u7269":"\ud83c\udf81","\u62e5\u62b1":"\ud83e\udd17","\u5f3a ":"\ud83d\udc4d","\u5f31":"\ud83d\udc4e","\u63e1\u624b":"\ud83d\udc4d","\u80dc\u5229":"\u270c","\u62b1\u62f3":"\u270a","\u52fe\u5f15":"\u270c","\u62f3\u5934":"\u270a","\u5dee\u52b2":"\u270c","\u7231\u4f60":"\u270c","NO":"\u270c","OK":"\ud83d\ude42","\u563f\u54c8":"\ud83d\ude42","\u6342\u8138":"\ud83d\ude42","\u5978\u7b11":"\ud83d\ude42","\u673a\u667a":"\ud83d\ude42","\u76b1\u7709":"\ud83d\ude42","\u8036":"\ud83d\ude42","\u5403\u74dc":"\ud83d\ude42","\u52a0\u6cb9":"\ud83d\ude42","\u6c57":"\ud83d\ude42","\u5929\u554a":"\ud83d\udc4c","\u793e\u4f1a\u793e\u4f1a":"\ud83d\ude42","\u65fa\u67f4":"\ud83d\ude42","\u597d\u7684":"\ud83d\ude42","\u54c7":"\ud83d\ude42"}""")

            except Exception as e:
                context["error"] = repr(e)
        elif 'advanced' in load_template:
            try:
                all_settings = SettingModel.objects.all()
                context["settings"] = list()
                for setting in all_settings:
                    context["settings"].append({"name": setting.name, "content": setting.content})
                context["settings"].sort(key=lambda elem: elem["name"])  # 按字段名升序排序
                context["settings_number"] = len(context["settings"])
                context["page_number"] = context["settings_number"] // 15 + 1
            except Exception as e:
                context["error"] = repr(e)
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as error:
        html_template = loader.get_template('home/page-500.html')
        context["error"] = error
        return HttpResponse(html_template.render(context, request))
