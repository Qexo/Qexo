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
