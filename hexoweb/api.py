from .functions import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
import requests
from .models import ImageModel
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from core.settings import QEXO_VERSION
from datetime import timezone, timedelta
from time import time


# API
def auth(request):
    try:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            context = {"msg": "登录成功，等待转跳", "status": True}
        else:
            context = {"msg": "登录信息错误", "status": False}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def set_github(request):
    try:
        repo = request.POST.get("repo")
        branch = request.POST.get("branch")
        token = request.POST.get("token")
        if not token:
            try:
                token = SettingModel.objects.get(name="GH_TOKEN").content
            except:
                pass
        path = request.POST.get("path")
        try:
            _repo = github.Github(token).get_repo(repo).get_contents(path + "source/_posts",
                                                                     ref=branch)
            save_setting("GH_REPO_PATH", path)
            save_setting("GH_REPO_BRANCH", branch)
            save_setting("GH_REPO", repo)
            save_setting("GH_TOKEN", token)
            context = {"msg": "保存成功!", "status": True}
        except:
            context = {"msg": "校验失败!", "status": False}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def set_update(request):
    try:
        update_repo = request.POST.get("repo")
        update_token = request.POST.get("token")
        update_branch = request.POST.get("branch")
        origin_branch = request.POST.get("origin")
        if not update_token:
            try:
                update_token = SettingModel.objects.get(name="UPDATE_TOKEN").content
            except:
                context = {"msg": "校验失败!", "status": False}
                return render(request, 'layouts/json.html', {"data": json.dumps(context)})
        try:
            user = github.Github(update_token)
            user.get_repo(update_repo).get_contents("", ref=update_branch)
            user.get_repo("am-abudu/Qexo").get_contents("", ref=origin_branch)
        except:
            context = {"msg": "校验失败!", "status": False}
            return render(request, 'layouts/json.html', {"data": json.dumps(context)})
        save_setting("UPDATE_REPO", update_repo)
        save_setting("UPDATE_TOKEN", update_token)
        save_setting("UPDATE_REPO_BRANCH", update_branch)
        save_setting("UPDATE_ORIGIN_BRANCH", origin_branch)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})

@login_required(login_url="/login/")
def set_api_key(request):
    try:
        apikey = request.POST.get("apikey")
        if apikey:
            save_setting("WEBHOOK_APIKEY", apikey)
        else:
            save_setting("WEBHOOK_APIKEY", ''.join(
                random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12)))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def set_image_bed(request):
    try:
        api = request.POST.get("api")
        post_params = request.POST.get("post")
        json_path = request.POST.get("jsonpath")
        custom_body = request.POST.get("body")
        custom_header = request.POST.get("header")
        custom_url = request.POST.get("custom")
        save_setting("IMG_API", api)
        save_setting("IMG_POST", post_params)
        save_setting("IMG_JSON_PATH", json_path)
        save_setting("IMG_CUSTOM_BODY", custom_body)
        save_setting("IMG_CUSTOM_HEADER", custom_header)
        save_setting("IMG_CUSTOM_URL", custom_url)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def set_user(request):
    try:
        password = request.POST.get("password")
        username = request.POST.get("username")
        newpassword = request.POST.get("newpassword")
        repassword = request.POST.get("repassword")
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            if repassword != newpassword:
                context = {"msg": "两次密码不一致!", "status": False}
                return render(request, 'layouts/json.html', {"data": json.dumps(context)})
            if not newpassword:
                context = {"msg": "请输入正确的密码！", "status": False}
                return render(request, 'layouts/json.html', {"data": json.dumps(context)})
            if not username:
                context = {"msg": "请输入正确的用户名！", "status": False}
                return render(request, 'layouts/json.html', {"data": json.dumps(context)})
            u = User.objects.get(username__exact=request.user.username)
            u.delete()
            User.objects.create_superuser(username=username, password=newpassword)
            context = {"msg": "保存成功！请重新登录", "status": True}
        else:
            context = {"msg": "原密码错误!", "status": False}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def do_update(request):
    repo = SettingModel.objects.get(name="UPDATE_REPO").content
    token = SettingModel.objects.get(name="UPDATE_TOKEN").content
    branch = SettingModel.objects.get(name="UPDATE_REPO_BRANCH").content
    repo = github.Github(token).get_repo(repo)
    origin_branch = SettingModel.objects.get(name="UPDATE_ORIGIN_BRANCH").content
    try:
        pull = repo.create_pull(title="Update from {}".format(QEXO_VERSION), body="auto update",
                                head="am-abudu:"+origin_branch,
                                base=branch, maintainer_can_modify=False)
        pull.merge()
        context = {"msg": "OK!", "status": True}
    except Exception as error:
        try:
            msg = json.loads(str(error)[4:])["errors"][0]["message"]
        except:
            msg = repr(error)
        context = {"msg": msg, "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def save(request):
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = request.POST.get('file')
        content = request.POST.get('content')
        try:
            repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
            branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
            repo.update_file(repo_path + file_path, "Update by Qexo", content,
                             repo.get_contents(repo_path + file_path, ref=branch).sha,
                             branch=branch)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def save_post(request):
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
                repo.delete_file(repo_path + "source/_drafts/" + file_name, "Delete by Qexo",
                                 repo.get_contents(repo_path + "source/_drafts/" + file_name,
                                                   ref=branch).sha,
                                 branch=branch)
            except:
                pass
            # 创建/更新文章
            try:
                repo.update_file(repo_path + "source/_posts/" + file_name, "Update by Qexo",
                                 content,
                                 repo.get_contents(repo_path + "source/_posts/" + file_name,
                                                   ref=branch).sha, branch=branch)
            except:
                repo.create_file(repo_path + "source/_posts/" + file_name, "Update by Qexo",
                                 content, branch=branch)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def save_draft(request):
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
                repo.update_file(repo_path + "source/_drafts/" + file_name, "Update by Qexo",
                                 content,
                                 repo.get_contents(repo_path + "source/_drafts/" + file_name,
                                                   ref=branch).sha, branch=branch)
            except:
                repo.create_file(repo_path + "source/_drafts/" + file_name, "Update by Qexo",
                                 content, branch=branch)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def new(request):
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        file_path = request.POST.get('file')
        content = request.POST.get('content')
        try:
            repo.create_file(path=SettingModel.objects.get(name="GH_REPO_PATH").content + file_path,
                             message="Create by Qexo", content=content,
                             branch=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
            context = {"msg": "OK!", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def delete(request):
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
        repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
        file_path = request.POST.get('file')
        try:
            file = repo.get_contents(file_path, ref=branch)
            if not isinstance(file, list):
                repo.delete_file(repo_path + file_path, "Delete by Qexo", file.sha, branch=branch)

            else:
                for i in file:
                    repo.delete_file(repo_path + i.path, "Delete by Qexo", i.sha, branch=branch)
            context = {"msg": "OK!", "status": True}
            # Delete Caches
            if ("_posts" in file_path) or ("_drafts" in file_path):
                delete_posts_caches()
            else:
                delete_all_caches()
        except Exception as error:
            context = {"msg": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def delete_post(request):
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
        repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
        filename = request.POST.get('file')
        try:
            repo.delete_file(repo_path + "source/_posts/" + filename, "Delete by Qexo",
                             repo.get_contents(
                                 repo_path + "source/_posts/" + filename, ref=branch).sha,
                             branch=branch)
            try:
                repo.delete_file(repo_path + "source/_drafts/" + filename, "Delete by Qexo",
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


@login_required(login_url="/login/")
def delete_img(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        image_date = request.POST.get('image')
        try:
            image = ImageModel.objects.get(date=image_date)
            image.delete()
            context = {"msg": "删除成功！", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def purge(request):
    context = dict(msg="Error!", status=False)
    try:
        delete_all_caches()
        context = {"msg": "清除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def create_webhook_config(request):
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


@csrf_exempt
def webhook(request):
    context = dict(msg="Error!", status=False)
    try:
        if request.GET.get("token") == SettingModel.objects.get(name="WEBHOOK_APIKEY").content:
            delete_all_caches()
            context = {"msg": "操作成功！", "status": True}
        else:
            context = {"msg": "校验错误", "status": False}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@csrf_exempt
@login_required(login_url="/login/")
def upload_img(request):
    context = dict(msg="上传失败！", url=False)
    if request.method == "POST":
        file = request.FILES.getlist('file[]')[0]
        try:
            api = SettingModel.objects.get(name="IMG_API").content
            post_params = SettingModel.objects.get(name="IMG_POST").content
            json_path = SettingModel.objects.get(name="IMG_JSON_PATH").content
            custom_body = SettingModel.objects.get(name="IMG_CUSTOM_BODY").content
            custom_header = SettingModel.objects.get(name="IMG_CUSTOM_HEADER").content
            custom_url = SettingModel.objects.get(name="IMG_CUSTOM_URL").content
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
                context["url"] = str(custom_url) + data
                context["msg"] = "上传成功！"
                context["status"] = True
            else:
                context["url"] = str(custom_url) + response.text
                context["msg"] = "上传成功！"
                context["status"] = True
            image = ImageModel()
            image.name = file.name
            image.url = context["url"]
            image.size = file.size
            image.type = file.content_type
            image.date = time()
            image.save()
        except Exception as error:
            context = {"msg": repr(error), "url": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def get_update(request):
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
        context["newer_text"] = latest.body
        context["status"] = True
    except:
        context["status"] = False
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})
