from .functions import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
import requests
from .models import ImageModel
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from core.QexoSettings import QEXO_VERSION
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


# 设置 OnePush api/set_onepush
@login_required(login_url="/login/")
def set_onepush(request):
    try:
        onepush = request.POST.get("onepush")
        save_setting("ONEPUSH", onepush)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 测试 OnePush api/test_onepush
@login_required(login_url="/login/")
def test_onepush(request):
    try:
        onepush = json.loads(request.POST.get("onepush"))
        ntfy = notify(onepush["notifier"], **onepush["params"], title="Qexo消息测试", content="如果你收到了这则消息, 那么代表您的消息配置成功了")
        try:
            data = ntfy.text
        except:
            data = "OK"
        context = {"msg": data, "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置API api/setapi
@login_required(login_url="/login/")
def set_api(request):
    try:
        apikey = request.POST.get("apikey")
        if apikey:
            save_setting("WEBHOOK_APIKEY", apikey)
        else:
            if not SettingModel.objects.filter(name="WEBHOOK_APIKEY").count():
                save_setting("WEBHOOK_APIKEY", ''.join(
                    random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12)))
        save_setting("ALLOW_FRIEND", request.POST.get("allow_friend"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置图床配置 api/set_image_bed
@login_required(login_url="/login/")
def set_image_bed(request):
    try:
        imageType = request.POST.get("imageType")
        if imageType == "custom":
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
            save_setting("IMG_TYPE", "custom")
        if imageType == "s3":
            key_id = request.POST.get("key-id")
            access_key = request.POST.get("access-key")
            bucket = request.POST.get("bucket")
            endpoint = request.POST.get("endpoint")
            path = request.POST.get("path")
            url = request.POST.get("url")
            save_setting("S3_KEY_ID", key_id)
            save_setting("S3_ACCESS_KEY", access_key)
            save_setting("S3_BUCKET", bucket)
            save_setting("S3_ENDPOINT", endpoint)
            save_setting("S3_PATH", path)
            save_setting("S3_PREV_URL", url)
            save_setting("IMG_TYPE", "s3")
        if imageType == "ftp":
            host = request.POST.get("FTP_HOST")
            port = request.POST.get("FTP_PORT")
            user = request.POST.get("FTP_USER")
            password = request.POST.get("FTP_PASS")
            path = request.POST.get("FTP_PATH")
            prev_url = request.POST.get("FTP_PREV_URL")
            save_setting("FTP_HOST", host)
            save_setting("FTP_PORT", port)
            save_setting("FTP_USER", user)
            save_setting("FTP_PASS", password)
            save_setting("FTP_PATH", path)
            save_setting("FTP_PREV_URL", prev_url)
            save_setting("IMG_TYPE", "ftp")
        if imageType == "":
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


# 设置统计配置 api/set_statistic
@login_required(login_url="/login/")
def set_statistic(request):
    try:
        domains = request.POST.get("statistic_domains")
        allow = request.POST.get("allow_statistic")
        save_setting("STATISTIC_ALLOW", allow)
        save_setting("STATISTIC_DOMAINS", domains)
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置 CustomModel 的字段 api/set_custom
@login_required(login_url="/login/")
def set_custom(request):
    try:
        save_custom(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 设置 CustomModel 的字段 api/del_custom
@login_required(login_url="/login/")
def del_custom(request):
    try:
        CustomModel.objects.filter(name=request.POST.get("name")).delete()
        context = {"msg": "删除成功!", "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 新建 CustomModel 的字段 api/new_custom
@login_required(login_url="/login/")
def new_custom(request):
    try:
        save_custom(request.POST.get("name"), request.POST.get("content"))
        context = {"msg": "保存成功!", "status": True}
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
            if img_type == "custom":
                api = SettingModel.objects.get(name="IMG_API").content
                post_params = SettingModel.objects.get(name="IMG_POST").content
                json_path = SettingModel.objects.get(name="IMG_JSON_PATH").content
                custom_body = SettingModel.objects.get(name="IMG_CUSTOM_BODY").content
                custom_header = SettingModel.objects.get(name="IMG_CUSTOM_HEADER").content
                custom_url = SettingModel.objects.get(name="IMG_CUSTOM_URL").content
                context["url"] = upload_to_custom(file, api, post_params, json_path, custom_body, custom_header, custom_url)
                context["msg"] = "上传成功！"
                context["status"] = True
            if img_type == "ftp":
                context["url"] = upload_to_ftp(file,
                                               SettingModel.objects.get(name="FTP_HOST").content,
                                               SettingModel.objects.get(name="FTP_PORT").content,
                                               SettingModel.objects.get(name="FTP_USER").content,
                                               SettingModel.objects.get(name="FTP_PASS").content,
                                               SettingModel.objects.get(name="FTP_PATH").content,
                                               SettingModel.objects.get(name="FTP_PREV_URL").content)
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
        friend.status = request.POST.get("status") == "显示"
        friend.save()
        context = {"msg": "修改成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 清理隐藏友链 api/clean_friend
@login_required(login_url="/login/")
def clean_friend(request):
    try:
        counter = 0
        all_friends = FriendModel.objects.all()
        for friend in all_friends:
            if not friend.status:
                friend.delete()
                counter += 1
        context = {"msg": "成功清理了{}条友链".format(counter) if counter else "无隐藏的友链", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 删除友链 api/del_friend
@login_required(login_url="/login/")
def del_friend(request):
    try:
        friend = FriendModel.objects.get(time=request.POST.get("time"))
        friend.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取全部消息 api/get_notifications
@login_required(login_url="/login/")
def get_notifications(request):
    try:
        # 检查更新
        latest = get_latest_version()
        cache = Cache.objects.filter(name="update")
        if cache.count():
            if (cache.first().content != latest["newer_time"]) and latest["hasNew"]:
                CreateNotification("程序更新", "检测到更新: " + latest["newer"] + "<br>" + latest[
                    "newer_text"] + "<p class=\"text-sm mb-0\">可前往 <object><a href=\"/settings.html\">设置</a></object> 在线更新</p>", time())
                save_cache("update", latest["newer_time"])
        else:
            if latest["hasNew"]:
                CreateNotification("程序更新", "检测到更新: " + latest["newer"] + "<br>" + latest[
                    "newer_text"] + "<p class=\"text-sm mb-0\">可前往 <object><a href=\"/settings.html\">设置</a></object> 在线更新</p>", time())
                save_cache("update", latest["newer_time"])
        context = {"data": GetNotifications(), "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 删除指定消息 api/del_notifications
@login_required(login_url="/login/")
def del_notification(request):
    try:
        DelNotification(request.POST.get("time"))
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 清理全部消息 api/clear_notifications
@login_required(login_url="/login/")
def clear_notification(request):
    try:
        all_notify = NotificationModel.objects.all()
        for N in all_notify:
            N.delete()
        context = {"msg": "删除成功！", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})
