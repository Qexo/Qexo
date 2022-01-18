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


# 登录验证 API api/auth
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


# 设置 Github 配置 api/set_github
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


# 设置APIKEY api/set_apikey
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


# 设置图床配置 api/set_image_bed
@login_required(login_url="/login/")
def set_image_bed(request):
    try:
        api = request.POST.get("api")
        post_params = request.POST.get("post")
        json_path = request.POST.get("jsonpath")
        custom_body = request.POST.get("body")
        custom_header = request.POST.get("header")
        custom_url = request.POST.get("custom")
        status = request.POST.get("cust-status")
        save_setting("IMG_API", api)
        save_setting("IMG_POST", post_params)
        save_setting("IMG_JSON_PATH", json_path)
        save_setting("IMG_CUSTOM_BODY", custom_body)
        save_setting("IMG_CUSTOM_HEADER", custom_header)
        save_setting("IMG_CUSTOM_URL", custom_url)
        if status == "on":
            save_setting("IMG_TYPE", "custom")
        else:
            if SettingModel.objects.get(name="IMG_TYPE").content == "custom":
                save_setting("IMG_TYPE", "")
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置 Abbrlink 配置 api/set_abbrlink
@login_required(login_url="/login/")
def set_abbrlink(request):
    try:
        alg = request.POST.get("alg")
        rep = request.POST.get("rep")
        save_setting("ABBRLINK_ALG", alg)
        save_setting("ABBRLINK_REP", rep)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置s3配置 api/set_s3
@login_required(login_url="/login/")
def set_s3(request):
    try:
        key_id = request.POST.get("key-id")
        access_key = request.POST.get("access-key")
        bucket = request.POST.get("bucket")
        endpoint = request.POST.get("endpoint")
        path = request.POST.get("path")
        url = request.POST.get("url")
        status = request.POST.get("s3-status")
        save_setting("S3_KEY_ID", key_id)
        save_setting("S3_ACCESS_KEY", access_key)
        save_setting("S3_BUCKET", bucket)
        save_setting("S3_ENDPOINT", endpoint)
        save_setting("S3_PATH", path)
        save_setting("S3_PREV_URL", url)
        if status == "on":
            save_setting("IMG_TYPE", "s3")
        else:
            if SettingModel.objects.get(name="IMG_TYPE").content == "s3":
                save_setting("IMG_TYPE", "")
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置自定义配置 api/set_cust
@login_required(login_url="/login/")
def set_cust(request):
    try:
        site_name = request.POST.get("name")
        split_word = request.POST.get("split")
        logo = request.POST.get("logo")
        icon = request.POST.get("icon")
        save_setting("QEXO_NAME", site_name)
        save_setting("QEXO_SPLIT", split_word)
        save_setting("QEXO_LOGO", logo)
        save_setting("QEXO_ICON", icon)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置用户信息 api/set_user
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


# 设置 SettingsModel 的字段 api/set_value
@login_required(login_url="/login/")
def set_value(request):
    try:
        save_setting(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置 SettingsModel 的字段 api/del_value
@login_required(login_url="/login/")
def del_value(request):
    try:
        SettingModel.objects.filter(name=request.POST.get("name")).delete()
        context = {"msg": "删除成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 新建 SettingsModel 的字段 api/new_value
@login_required(login_url="/login/")
def new_value(request):
    try:
        save_setting(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 自动修复程序 api/fix
@login_required(login_url="/login/")
def auto_fix(request):
    try:
        counter = fix_all()
        msg = "尝试自动修复了 {} 个字段，请在稍后检查和修改配置".format(counter)
        context = {"msg": msg, "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 执行更新 api/do_update
@login_required(login_url="/login/")
def do_update(request):
    branch = request.POST.get("branch")
    try:
        res = OnekeyUpdate(branch=branch)
        if res["status"]:
            save_setting("UPDATE_FROM", QEXO_VERSION)
            context = {"msg": "OK!", "status": True}
        else:
            context = {"msg": res["msg"], "status": False}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 保存内容 api/save
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


# 保存文章 api/save_post
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


# 保存草稿 api/save_draft
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


# 新建内容 api/new
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


# 删除内容 api/delete
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


# 删除文章 api/delete_post
@login_required(login_url="/login/")
def delete_post(request):
    repo = get_repo()
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
        repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
        filename = request.POST.get('file')
        try:
            try:
                repo.delete_file(repo_path + "source/_posts/" + filename, "Delete by Qexo",
                                 repo.get_contents(
                                     repo_path + "source/_posts/" + filename, ref=branch).sha,
                                 branch=branch)
            except:
                pass
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


# 删除图片记录 api/delete_img
@login_required(login_url="/login/")
def delete_img(request):
    context = dict(msg="Error!", status=False)
    if request.method == "POST":
        image_date = request.POST.get('image')
        try:
            image = ImageModel.objects.filter(date=image_date)
            image.delete()
            context = {"msg": "删除成功！", "status": True}
        except Exception as error:
            context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 清除缓存 api/purge
@login_required(login_url="/login/")
def purge(request):
    try:
        delete_all_caches()
        context = {"msg": "清除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 自动设置 Webhook 事件 api/create_webhook
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


# Webhook api/webhook
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


# 上传图片 api/upload
@csrf_exempt
@login_required(login_url="/login/")
def upload_img(request):
    context = dict(msg="上传失败！", url=False)
    if request.method == "POST":
        file = request.FILES.getlist('file[]')[0]
        try:
            try:
                img_type = SettingModel.objects.get(name="IMG_TYPE").content
            except:
                save_setting("IMG_TYPE", "cust")
                img_type = "cust"
            if img_type == "s3":
                context["url"] = upload_to_s3(file,
                                              SettingModel.objects.get(name="S3_KEY_ID").content,
                                              SettingModel.objects.get(
                                                  name="S3_ACCESS_KEY").content,
                                              SettingModel.objects.get(name="S3_ENDPOINT").content,
                                              SettingModel.objects.get(name="S3_BUCKET").content,
                                              SettingModel.objects.get(name="S3_PATH").content,
                                              SettingModel.objects.get(name="S3_PREV_URL").content)
                context["msg"] = "上传成功！"
                context["status"] = True
            else:
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


# 获取更新 api/get_update
@login_required(login_url="/login/")
def get_update(request):
    return render(request, 'layouts/json.html', {"data": json.dumps(get_latest_version())})


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
        friend.save()
        context = {"msg": "添加成功！", "time": friend.time, "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})

# 修改友链 api/edit_friend
@login_required(login_url="/login/")
def edit_friend(request):
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.name = request.POST.get("name")
        friend.url = request.POST.get("url")
        friend.imageUrl = request.POST.get("image")
        friend.description = request.POST.get("description")
        friend.save()
        context = {"msg": "修改成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


@login_required(login_url="/login/")
def del_friend(request):
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})
