# -*- encoding: utf-8 -*-
"""
自定义装饰器模块
提供权限检查、错误处理等装饰器
"""
import logging
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect


def staff_required(redirect_to_login=True):
    """
    检查用户是否为管理员的装饰器
    
    Args:
        redirect_to_login: 是否重定向到登录页（用于web视图），False则返回JSON（用于API）
    
    Usage:
        @staff_required()
        def my_view(request):
            ...
            
        @staff_required(redirect_to_login=False)
        def my_api(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_to_login:
                    return redirect("/login/")
                else:
                    return JsonResponse(
                        safe=False, 
                        data={"msg": "未登录", "status": False}
                    )
            
            if not request.user.is_staff:
                from hexoweb.functions import gettext
                logging.info(
                    gettext("USER_IS_NOT_STAFF").format(
                        request.user.username, 
                        request.path
                    )
                )
                if redirect_to_login:
                    from hexoweb.views import page_403
                    return page_403(request, gettext("NO_PERMISSION"))
                else:
                    return JsonResponse(
                        safe=False, 
                        data={"msg": gettext("NO_PERMISSION"), "status": False}
                    )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def init_not_completed(redirect_to_login=False):
    """
    检查初始化是否未完成的装饰器
    防止已完成初始化的系统再次启动初始化流程
    
    Args:
        redirect_to_login: 是否重定向到登录页（用于web视图），False则返回JSON（用于API）
    
    Usage:
        @init_not_completed()
        def init_api(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            from hexoweb.functions import gettext
            from hexoweb.models import SettingModel
            
            # 权限检查直接读取数据库，避免其他进程完成初始化后仍使用旧缓存。
            init_value = SettingModel.objects.get_content_by_name("INIT")
            try:
                current_init = int(init_value) if init_value else 1
            except (ValueError, TypeError):
                current_init = 1
            
            # 如果初始化已完成（INIT >= 6），拒绝访问
            if current_init >= 6:
                logging.warning(
                    "Attempt to access init API/view after initialization is complete. "
                    "Current INIT: %s, User IP: %s, Path: %s",
                    current_init,
                    request.META.get("REMOTE_ADDR", "unknown"),
                    request.path
                )
                
                if redirect_to_login:
                    return redirect("/login/")
                else:
                    return JsonResponse(
                        safe=False,
                        data={
                            "msg": gettext("INIT_ALREADY_COMPLETED") or "初始化已完成，无法再次进行",
                            "status": False
                        },
                        status=403
                    )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def api_auth_required(func):
    """
    检查API Token鉴权的装饰器（用于公共API）
    
    验证请求中的token参数（GET或POST），使用SHA-256哈希比对
    用于 /pub/* 等公共API接口
    
    Usage:
        @api_auth_required
        def my_public_api(request):
            ...
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        from hexoweb.functions import check_if_api_auth, gettext
        
        if not check_if_api_auth(request):
            return JsonResponse(
                safe=False, 
                data={"msg": gettext("AUTH_FAILED"), "status": False}
            )
        
        return func(request, *args, **kwargs)
    return wrapper
