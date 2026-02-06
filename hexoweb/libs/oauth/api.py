import logging

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from hexoweb.functions import gettext


# api/oauth/callback/<provider_name>
def oauth_callback(request, provider_name: str):
    """
    OAuth Authorize Callback endpoint
    :param request: Django request object
    :param provider_name: OAuth provider name, please make sure it was defined in OAUTH_PROVIDERS env.
    """
    from authlib.oidc.core.claims import UserInfo
    from .models import OAuthIdentity
    from django.db import IntegrityError
    from django.utils.timezone import now
    from .functions import create_oauth_callback_action, get_oauth_providers_object, OAuthError

    @login_required(login_url="/login/")
    # Ensure the signature of __handle_bind is match to decorator`s design
    # I know that I can access request object of the parent function in this child function
    def __handle_bind(parent_request, userinfo: UserInfo):
        oauth_identity = OAuthIdentity(
            provider_name=provider_name,
            provider_sub=userinfo.sub,
            provider_preferred_username=userinfo.preferred_username,
            local_user=parent_request.user,
            bind_time=now()
        )
        try:
            oauth_identity.save()
            return create_oauth_callback_action(parent_request, True, gettext("OAUTH_IDENTITY_BIND_SUCCESS"), 'refresh')
        except IntegrityError:
            # Because we use provider_name and provider_sub as joint constraint of OAuthIdentity models,
            # when an existing third-party identity account is trying to be bound,
            # Django will throw IntegrityError.
            return create_oauth_callback_action(parent_request, False, gettext("OAUTH_IDENTITY_ALREADY_EXISTED"),
                                                'none')

    def __handle_login(userinfo: UserInfo):
        oauth_identity = OAuthIdentity.objects.filter(provider_name=provider_name, provider_sub=userinfo.sub).first()
        if oauth_identity:
            oauth_identity.local_user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, oauth_identity.local_user)
            return create_oauth_callback_action(request, True, gettext("OAUTH_LOGIN_SUCCESS"), 'refresh')
        else:
            return create_oauth_callback_action(request, False, gettext("OAUTH_UNKNOWN_IDENTITY"), 'none')

    oauth_providers = get_oauth_providers_object()
    if oauth_providers and oauth_providers.get(provider_name):
        try:
            # Trying to fetch user`s info from provider
            provider = oauth_providers.get(provider_name)
            token = provider.authorize_access_token(request)
            user = provider.userinfo(token=token)

            match request.GET.get('action'):
                case 'bind':
                    return __handle_bind(request, user)
                case 'login':
                    return __handle_login(user)
        except OAuthError:
            return create_oauth_callback_action(request, False, gettext('OAUTH_DENIED_AUTHORIZATION'), 'none')
        except Exception as error:
            # If we meet unknown errors
            logging.error(repr(error))
            return create_oauth_callback_action(request, False, repr(error), 'none')

    else:
        # If we meet an unknown provider
        return create_oauth_callback_action(request, False, gettext("OAUTH_UNKNOWN_PROVIDER"), 'none')


# api/oauth/list
@login_required(login_url="/login/")
def oauth_list(request):
    """
    Lookup user`s third-party identities
    """
    from .functions import get_oauth_providers_list
    context = dict(msg="Error!", status=False, data={})
    data = {}
    if request.method == "GET":
        try:
            from .models import OAuthIdentity
            user_identities = request.user.oauth_identities.all()
            for item in user_identities:
                data[item.provider_name] = {
                    "provider_sub": item.provider_sub,
                    "provider_preferred_username": item.provider_preferred_username,
                    "bind_time": item.bind_time
                }
            context["msg"] = 'OK'
            context["status"] = True
            context['data'] = dict(providers=get_oauth_providers_list(), linked=data)
        except Exception as error:
            logging.error(repr(error))
            context["msg"] = repr(error)

    return JsonResponse(safe=False, data=context)


# api/oauth/link/<provider_name>
@login_required(login_url="/login/")
def oauth_link(request, provider_name):
    from django.urls import reverse
    from django.utils.http import urlencode
    from .functions import get_oauth_providers_object, create_oauth_callback_action
    """
    Bind a third-party identity to user
    """
    oauth_providers = get_oauth_providers_object()
    if oauth_providers and oauth_providers.get(provider_name):
        # Make sure provider is existing
        try:
            provider = oauth_providers.get(provider_name)
            base_callback_path = reverse('oauth_callback', kwargs={'provider_name': provider_name})
            redirect_uri = request.build_absolute_uri(base_callback_path)
            redirect_uri += f"?{urlencode({'action': 'bind'})}"
            return provider.authorize_redirect(request, redirect_uri)
        except Exception as error:
            logging.error(repr(error))
            return create_oauth_callback_action(request, False, repr(error), 'none')
    return create_oauth_callback_action(request, False, gettext("OAUTH_UNKNOWN_PROVIDER"), 'none')


# api/oauth/unlink/<provider_name>
@login_required(login_url="/login/")
def oauth_unlink(request, provider_name):
    """
    Unbind a third-party identity to user
    """
    context = dict(msg="Error!", status=False)
    from .functions import check_sso_only
    if request.method == "GET":
        identity = request.user.oauth_identities.filter(provider_name=provider_name).first()
        if check_sso_only() and request.user.oauth_identities.count() <= 1:
            context['msg'] = gettext("OAUTH_ONLY_ONE_IDENTITY_EXIST")
        elif identity:
            identity.delete()
            context['msg'] = gettext("OAUTH_UNBIND_SUCCESS")
            context['status'] = True
        else:
            context['msg'] = gettext("OAUTH_UNBIND_FAILED")
    return JsonResponse(safe=False, data=context)


# api/oauth/login/<provider_name>
def oauth_login(request, provider_name):
    """
    Use OAuth/OIDC identity to login user
    :param request: Django request object
    :param provider_name: OAuth Provider name, please make sure it exists
    """
    from django.urls import reverse
    from django.utils.http import urlencode
    from .functions import get_oauth_providers_object, create_oauth_callback_action
    oauth_providers = get_oauth_providers_object()
    if oauth_providers and oauth_providers.get(provider_name):
        try:
            provider = oauth_providers.get(provider_name)
            base_callback_path = reverse('oauth_callback', kwargs={'provider_name': provider_name})
            redirect_uri = request.build_absolute_uri(base_callback_path)
            redirect_uri += f"?{urlencode({'action': 'login'})}"
            return provider.authorize_redirect(request, redirect_uri)
        except Exception as error:
            logging.error(repr(error))
            return create_oauth_callback_action(request, False, repr(error), 'none')
    else:
        return create_oauth_callback_action(request, False, gettext('OAUTH_UNKNOWN_PROVIDER'), 'none')
