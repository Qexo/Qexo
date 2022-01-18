from .functions import *
from django.views.decorators.csrf import csrf_exempt
import random
import requests
from .models import ImageModel
from django.shortcuts import render
from time import strftime, localtime
from time import time


# 保存内容 pub/save
@csrf_exempt
def save(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 保存文章 pub/save_post
@csrf_exempt
def save_post(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 保存草稿 pub/save_draft
@csrf_exempt
def save_draft(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 新建内容 pub/new
@csrf_exempt
def new(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 删除内容 pub/delete
@csrf_exempt
def delete(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 删除文章 pub/delete_post
@csrf_exempt
def delete_post(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 自动设置 Webhook 事件 pub/create_webhook
@csrf_exempt
def create_webhook_config(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 上传图片 pub/upload
@csrf_exempt
def upload_img(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
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


# 获取更新 pub/get_update
@csrf_exempt
def get_update(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    return render(request, 'layouts/json.html', {"data": json.dumps(get_latest_version())})


# 获取所有文章 pub/get_posts
@csrf_exempt
def get_posts(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        cache = Cache.objects.filter(name="posts")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_posts_cache()
        context = {"status": True, "posts": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有页面 pub/get_pages
@csrf_exempt
def get_pages(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        cache = Cache.objects.filter(name="pages")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_pages_cache()
        context = {"status": True, "pages": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有配置 pub/get_configs
@csrf_exempt
def get_configs(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        cache = Cache.objects.filter(name="configs")
        if cache.count():
            posts = json.loads(cache.first().content)
        else:
            posts = update_configs_cache()
        context = {"status": True, "configs": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取所有图片 pub/get_images
@csrf_exempt
def get_images(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        posts = list()
        images = ImageModel.objects.all()
        for i in images:
            posts.append({"name": i.name, "size": int(i.size), "url": i.url,
                          "date": strftime("%Y-%m-%d %H:%M:%S",
                                           localtime(float(i.date))),
                          "time": i.date})
        context = {"status": True, "images": posts}
    except Exception as error:
        context = {"status": False, "error": repr(error)}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 自动修复程序 api/fix
@csrf_exempt
def auto_fix(request):
    if not check_if_api_auth(request):
        return render(request, 'layouts/json.html', {"data": json.dumps({"msg": "鉴权错误！",
                                                                         "status": False})})
    try:
        counter = fix_all()
        msg = "尝试自动修复了 {} 个字段，请在稍后检查和修改配置".format(counter)
        context = {"msg": msg, "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# 获取友情链接 pub/friends
@csrf_exempt
def friends(request):
    try:
        friends = FriendModel.objects.all()
        data = list()
        for i in friends:
            data.append({"name": i.name, "url": i.url, "image": i.imageUrl,
                          "description": i.description,
                          "time": i.time})
        context = {"data": data, "status": True}
    except Exception as e:
        context = {"msg": repr(e), "status": False}
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})
