# -*- encoding: utf-8 -*-
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm
from django import template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
from core.settings import QEXO_VERSION
import github
from django.template.defaulttags import register
import json
from .models import Cache, SettingModel, ImageModel
import time
import random
from datetime import datetime, timezone, timedelta


def get_repo():
    if SettingModel.objects.filter(name__contains="GH_").count() >= 4:
        repo = github.Github(SettingModel.objects.get(name='GH_TOKEN').content).get_repo(
            SettingModel.objects.get(name="GH_REPO").content)
        return repo
    return False


def get_post(post):
    repo_path = SettingModel.objects.get(name="GH_REPO_PATH").content
    branch = SettingModel.objects.get(name="GH_REPO_BRANCH").content
    try:
        return get_repo().get_contents(repo_path + "source/_drafts/" + post,
                                       branch).decoded_content.decode("utf8")
    except:
        return get_repo().get_contents(repo_path + "source/_posts/" + post,
                                       branch).decoded_content.decode("utf8")


@register.filter  # 在模板中使用range()
def get_range(value):
    return range(1, value + 1)


@register.filter
def div(value, div):  # 保留两位小数的除法
    return round((value / div), 2)


# 更新缓存
def update_caches(name, content, _type="json"):
    caches = Cache.objects.filter(name=name)
    if caches.count():
        caches.delete()
    posts_cache = Cache()
    posts_cache.name = name
    if _type == "json":
        posts_cache.content = json.dumps(content)
    else:
        posts_cache.content = content
    posts_cache.save()


def update_posts_cache(s=None, _path=""):
    repo = get_repo()

    if s:
        old_cache = Cache.objects.filter(name="posts")
        if old_cache.count():
            posts = json.loads(old_cache.first().content)
            i = 0
            while i < len(posts):
                if s not in posts[i]["name"]:
                    del posts[i]
                    i -= 1
                i += 1
            cache_name = "posts." + str(s)
            update_caches(cache_name, posts)
            return posts
    try:
        _posts = list()
        _drafts = list()
        names = list()
        posts = repo.get_contents(
            SettingModel.objects.get(name="GH_REPO_PATH").content + 'source/_posts' + _path,
            ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
        for i in range(len(posts)):
            if posts[i].type == "file":
                _posts.append(
                    {"name": posts[i].path.split("source/_posts/")[1][0:-3],
                     "fullname": posts[i].path.split("source/_posts/")[1],
                     "path": posts[i].path,
                     "size": posts[i].size,
                     "status": True})
                names.append(posts[i].path.split("source/_posts/")[1])
            if posts[i].type == "dir":
                dir_content = update_posts_cache(_path=posts[i].path.split("source/_posts")[1])
                for file in dir_content:
                    if "source/_posts" in file["path"]:
                        _posts.append(file)
                        names.append(file["fullname"])
    except:
        pass
    try:
        drafts = repo.get_contents(
            SettingModel.objects.get(name="GH_REPO_PATH").content + 'source/_drafts' + _path,
            ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
        for i in range(len(drafts)):
            if drafts[i].type == "file":
                if drafts[i].path.split(
                        "source/_drafts/")[1] not in names:
                    _drafts.append({"name": drafts[i].path.split(
                        "source/_drafts/")[1][0:-3], "fullname": drafts[i].path.split(
                        "source/_drafts/")[1],
                                    "path": drafts[i].path,
                                    "size": drafts[i].size, "status": False})
            if drafts[i].type == "dir":
                dir_content = update_posts_cache(_path=drafts[i].path.split("source/_drafts")[1])
                for file in dir_content:
                    if ("source/_drafts" in file["path"]) and (file["fullname"] not in names):
                        _posts.append(file)
                        names.append(file["fullname"])
    except:
        pass
    posts = _posts + _drafts
    if s:
        if not old_cache.count():
            update_caches("posts", posts)
        i = 0
        while i < len(posts):
            if s not in posts[i]["name"]:
                del posts[i]
                i -= 1
            i += 1
    if not _path:
        if s:
            cache_name = "posts." + str(s)
        else:
            cache_name = "posts"
        update_caches(cache_name, posts)
    return posts


def update_pages_cache(s=None):
    repo = get_repo()
    posts = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content + 'source',
                              ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    results = list()
    for post in posts:
        if post.type == "dir":
            for i in repo.get_contents(
                    SettingModel.objects.get(name="GH_REPO_PATH").content + post.path,
                    ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content):
                if i.type == "file":
                    if s:
                        if (i.name == "index.md" or i.name == "index.html") and (
                                str(s) in post.name):
                            results.append({"name": post.name, "path": i.path, "size": i.size})
                            break
                    else:
                        if i.name == "index.md" or i.name == "index.html":
                            results.append({"name": post.name, "path": i.path, "size": i.size})
                            break
    if s:
        cache_name = "pages." + str(s)
    else:
        cache_name = "pages"
    update_caches(cache_name, results)
    return results


def update_configs_cache(s=None):
    repo = get_repo()
    posts = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content,
                              ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    results = list()
    for post in posts:
        try:
            if s:
                if post.name[-3:] == "yml" and s in post.name:
                    results.append({"name": post.name, "path": post.path, "size": post.size})
            else:
                if post.name[-3:] == "yml":
                    results.append({"name": post.name, "path": post.path, "size": post.size})
        except:
            pass

    themes = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content + "themes",
                               ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    for theme in themes:
        if theme.type == "dir":
            for post in repo.get_contents(theme.path,
                                          ref=SettingModel.objects.get(
                                              name="GH_REPO_BRANCH").content):
                try:
                    if s:
                        if post.name[-3:] == "yml" and s in post.name:
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    else:
                        if post.name[-3:] == "yml":
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                except:
                    pass

    sources = repo.get_contents(SettingModel.objects.get(name="GH_REPO_PATH").content +
                                "source",
                                ref=SettingModel.objects.get(name="GH_REPO_BRANCH").content)
    for source in sources:
        if source.type == "file":
            try:
                if s:
                    if source.name[-3:] == "yml" and s in source.name:
                        results.append(
                            {"name": source.name, "path": source.path, "size": source.size})
                else:
                    if source.name[-3:] == "yml":
                        results.append(
                            {"name": source.name, "path": source.path, "size": source.size})
            except:
                pass
        if source.type == "dir":
            for post in repo.get_contents(source.path,
                                          ref=SettingModel.objects.get(
                                              name="GH_REPO_BRANCH").content):
                try:
                    if s:
                        if post.name[-3:] == "yml" and s in post.name:
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                    else:
                        if post.name[-3:] == "yml":
                            results.append(
                                {"name": post.name, "path": post.path, "size": post.size})
                except:
                    pass

    if s:
        cache_name = "configs." + str(s)
    else:
        cache_name = "configs"
    update_caches(cache_name, results)
    return results


def delete_all_caches():
    caches = Cache.objects.all()
    for cache in caches:
        cache.delete()


def delete_posts_caches():
    caches = Cache.objects.all()
    for cache in caches:
        if cache.name[:5] == "posts":
            cache.delete()


def delete_pages_caches():
    caches = Cache.objects.all()
    for cache in caches:
        try:
            name = cache.name[:5]
        except:
            name = ""
        if name == "pages":
            cache.delete()


def save_setting(name, content):
    obj = SettingModel.objects.filter(name=name)
    if obj.count() == 1:
        obj.delete()
    if obj.count() > 1:
        for i in obj:
            i.delete()
    new_set = SettingModel()
    new_set.name = str(name)
    if content is not None:
        new_set.content = str(content)
    else:
        new_set.content = ""
    new_set.save()
    return new_set


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    try:
        if int(SettingModel.objects.get(name="INIT").content) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                return redirect("/")
            else:
                msg = '登录信息错误'
        else:
            msg = '验证表单时出错'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def init_view(request):
    msg = None
    context = dict()
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
                username = request.POST.get("username")
                password = request.POST.get("password")
                repassword = request.POST.get("repassword")
                if repassword != password:
                    msg = "两次密码不一致!"
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                elif not password:
                    msg = "请输入正确的密码！"
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
                elif not username:
                    msg = "请输入正确的用户名！"
                    context["username"] = username
                    context["password"] = password
                    context["repassword"] = repassword
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

            apikey = request.POST.get("apikey")
            save_setting("WEBHOOK_APIKEY", apikey)
            update_repo = request.POST.get("repo")
            update_token = request.POST.get("token")
            update_branch = request.POST.get("branch")
            if update_branch and update_token and update_repo:
                try:
                    github.Github(update_token).get_repo(update_repo).get_contents("",
                                                                                   ref=update_branch)
                    save_setting("UPDATE_REPO", update_repo)
                    save_setting("UPDATE_TOKEN", update_token)
                    save_setting("UPDATE_REPO_BRANCH", update_branch)
                    save_setting("INIT", "6")
                    step = "6"
                except:
                    msg = "校验失败"
                    context["apikey"] = apikey
                    context["repo"] = update_repo
                    context["token"] = update_token
                    context["branch"] = update_branch
            else:
                save_setting("UPDATE_REPO", update_repo)
                save_setting("UPDATE_TOKEN", update_token)
                save_setting("UPDATE_REPO_BRANCH", update_branch)
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


# API
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
def set_others(request):
    try:
        apikey = request.POST.get("apikey")
        if apikey:
            save_setting("WEBHOOK_APIKEY", apikey)
        update_repo = request.POST.get("repo")
        update_token = request.POST.get("token")
        update_branch = request.POST.get("branch")
        try:
            if update_repo == SettingModel.objects.get(name="UPDATE_REPO") and \
                    update_branch == SettingModel.objects.get(name="UPDATE_BRANCH"):
                context = {"msg": "保存成功!", "status": True}
                return render(request, 'layouts/json.html', {"data": json.dumps(context)})
        except:
            pass
        if not update_token:
            try:
                update_token = SettingModel.objects.get(name="UPDATE_TOKEN").content
            except:
                context = {"msg": "校验失败!", "status": False}
                return render(request, 'layouts/json.html', {"data": json.dumps(context)})
        try:
            github.Github(update_token).get_repo(update_repo).get_contents("", ref=update_branch)
        except:
            context = {"msg": "校验失败!", "status": False}
            return render(request, 'layouts/json.html', {"data": json.dumps(context)})
        save_setting("UPDATE_REPO", update_repo)
        save_setting("UPDATE_TOKEN", update_token)
        save_setting("UPDATE_REPO_BRANCH", update_branch)
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
    context = dict(msg="Error!", status=False)
    try:
        pull = repo.create_pull(title="Update from {}".format(QEXO_VERSION), body="auto update",
                                head="am-abudu:master",
                                base=branch, maintainer_can_modify=False)
        pull.merge()
        context = {"msg": "OK!", "status": True}
    except Exception as error:
        context = {"msg": repr(error), "status": False}
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
            image.date = time.time()
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
        context["newer_link"] = latest.zipball_url
        context["newer_time"] = latest.created_at.astimezone(
            timezone(timedelta(hours=16))).strftime(
            "%Y-%m-%d %H:%M:%S")
        context["newer_text"] = latest.body
        context["status"] = True
    except:
        context["status"] = False
    return render(request, 'layouts/json.html', {"data": json.dumps(context)})


# Pages
@login_required(login_url="/login/")
def index(request):
    try:
        if int(SettingModel.objects.get(name="INIT").content) <= 5:
            return redirect("/init/")
    except:
        return redirect("/init/")
    context = {'segment': 'index'}
    cache = Cache.objects.filter(name="posts")
    if cache.count():
        posts = json.loads(cache.first().content)
    else:
        posts = update_posts_cache()
    _images = ImageModel.objects.all()
    images = list()
    for i in _images:
        images.append({"name": i.name, "size": int(i.size), "url": i.url,
                       "date": time.strftime("%Y-%m-%d", time.localtime(float(i.date)))})
    if len(posts) >= 5:
        context["posts"] = posts[0:5]
    else:
        context["posts"] = posts
    if len(images) >= 5:
        context["images"] = images[0:5]
    else:
        context["images"] = images
    user = github.Github(SettingModel.objects.get(name='GH_TOKEN').content)
    latest = user.get_repo("am-abudu/Qexo").get_latest_release()
    if latest.tag_name and (latest.tag_name != QEXO_VERSION):
        context["hasNew"] = True
    else:
        context["hasNew"] = False
    context["newer"] = latest.tag_name
    context["newer_link"] = latest.zipball_url
    context["newer_time"] = latest.created_at.astimezone(timezone(timedelta(hours=16))).strftime(
        "%Y-%m-%d %H:%M:%S")
    context["newer_text"] = latest.body
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
                ">", "\\>")
            context['filename'] = file_path.split("/")[-2] + "/" + file_path.split("/")[-1]
            context["file_path"] = file_path
            try:
                if SettingModel.objects.get(name="IMG_API").content and SettingModel.objects.get(
                        name="IMG_POST").content:
                    context["img_bed"] = True
            except:
                pass
        elif "edit_config" in load_template:
            file_path = request.GET.get("file")
            repo = get_repo()
            context["file_content"] = repr(repo.get_contents(
                SettingModel.objects.get(name="GH_REPO_PATH").content + file_path,
                ref=SettingModel.objects.get(
                    name="GH_REPO_BRANCH").content).decoded_content.decode(
                "utf8")).replace("<", "\\<").replace(">", "\\>")
            context["filepath"] = file_path
            context['filename'] = file_path.split("/")[-1]
        elif "edit" in load_template:
            file_path = request.GET.get("file")
            context["file_content"] = repr(get_post(file_path)).replace("<",
                                                                        "\\<").replace(
                ">", "\\>")
            context['filename'] = file_path.split("/")[-1]
            context['fullname'] = file_path
            try:
                if SettingModel.objects.get(name="IMG_API").content and SettingModel.objects.get(
                        name="IMG_POST").content:
                    context["img_bed"] = True
            except:
                pass
        elif "new_page" in load_template:
            repo = get_repo()
            try:
                context["file_content"] = repr(
                    repo.get_contents(
                        SettingModel.objects.get(name="GH_REPO_PATH").content + "scaffolds/page.md",
                        ref=SettingModel.objects.get(
                            name="GH_REPO_BRANCH").content).decoded_content.decode(
                        "utf8")).replace("<",
                                         "\\<").replace(
                    ">", "\\>").replace("{{ date }}", time.strftime("%Y-%m-%d %H:%M:%S",
                                                                    time.localtime(
                                                                        time.time())))

            except:
                pass
            try:
                if SettingModel.objects.get(name="IMG_API").content and SettingModel.objects.get(
                        name="IMG_POST").content:
                    context["img_bed"] = True
            except:
                pass
        elif "new" in load_template:
            repo = get_repo()
            try:
                context["file_content"] = repr(
                    repo.get_contents(
                        SettingModel.objects.get(name="GH_REPO_PATH").content + "scaffolds/post.md",
                        ref=SettingModel.objects.get(
                            name="GH_REPO_BRANCH").content).decoded_content.decode(
                        "utf8").replace("{{ date }}", time.strftime("%Y-%m-%d %H:%M:%S",
                                                                    time.localtime(
                                                                        time.time())))).replace("<",
                                                                                                "\\<").replace(
                    ">", "\\>")

            except:
                pass
            try:
                if SettingModel.objects.get(name="IMG_API").content and SettingModel.objects.get(
                        name="IMG_POST").content:
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
                                  "date": time.strftime("%Y-%m-%d %H:%M:%S",
                                                        time.localtime(float(i.date))),
                                  "time": i.date})
            else:
                images = ImageModel.objects.all()
                for i in images:
                    posts.append({"name": i.name, "size": int(i.size), "url": i.url,
                                  "date": time.strftime("%Y-%m-%d %H:%M:%S",
                                                        time.localtime(float(i.date))),
                                  "time": i.date})
            context["posts"] = posts
            context["post_number"] = len(posts)
            context["page_number"] = context["post_number"] // 15 + 1
            context["search"] = search
        elif 'settings' in load_template:
            try:
                context['GH_REPO_PATH'] = SettingModel.objects.get(name="GH_REPO_PATH").content
                context['GH_REPO_BRANCH'] = SettingModel.objects.get(name="GH_REPO_BRANCH").content
                context['GH_REPO'] = SettingModel.objects.get(name="GH_REPO").content
                context['GH_TOKEN'] = SettingModel.objects.get(name="GH_TOKEN").content
                token_len = len(context['GH_TOKEN'])
                if token_len >= 5:
                    context['GH_TOKEN'] = context['GH_TOKEN'][:3] + "*" * (token_len - 5) + \
                                          context['GH_TOKEN'][-1]
                context['IMG_CUSTOM_URL'] = SettingModel.objects.get(name='IMG_CUSTOM_URL').content
                context['IMG_CUSTOM_HEADER'] = SettingModel.objects.get(
                    name='IMG_CUSTOM_HEADER').content
                context['IMG_CUSTOM_BODY'] = SettingModel.objects.get(
                    name='IMG_CUSTOM_BODY').content
                context['IMG_JSON_PATH'] = SettingModel.objects.get(name='IMG_JSON_PATH').content
                context['IMG_POST'] = SettingModel.objects.get(name='IMG_POST').content
                context['IMG_API'] = SettingModel.objects.get(name='IMG_API').content
                context['UPDATE_REPO_BRANCH'] = SettingModel.objects.get(
                    name="UPDATE_REPO_BRANCH").content
                context['UPDATE_REPO'] = SettingModel.objects.get(name="UPDATE_REPO").content
                context['UPDATE_TOKEN'] = SettingModel.objects.get(name="UPDATE_TOKEN").content
                if len(context['UPDATE_TOKEN']) >= 5:
                    context['UPDATE_TOKEN'] = context['UPDATE_TOKEN'][:3] + "*" * (token_len - 5) \
                                              + context['UPDATE_TOKEN'][-1]
                user = github.Github(SettingModel.objects.get(name='GH_TOKEN').content)
                latest = user.get_repo("am-abudu/Qexo").get_latest_release()
                if latest.tag_name and (latest.tag_name != QEXO_VERSION):
                    context["hasNew"] = True
                else:
                    context["hasNew"] = False
                context["newer"] = latest.tag_name
                context["newer_link"] = latest.zipball_url
                context["newer_time"] = latest.created_at.astimezone(
                    timezone(timedelta(hours=16))).strftime(
                    "%Y-%m-%d %H:%M:%S")
                context["newer_text"] = latest.body
                context["version"] = QEXO_VERSION
                if context["hasNew"] and context['UPDATE_REPO_BRANCH'] and context['UPDATE_REPO'] \
                        and context['UPDATE_TOKEN']:
                    context["showUpdate"] = True
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
