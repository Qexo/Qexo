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
