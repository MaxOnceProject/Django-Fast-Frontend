from django.urls import get_resolver

import frontend
from django.conf import settings
from .sites import AccountFrontend


class Frontend(frontend.Config):
    login_required = getattr(settings, 'FRONTEND_LOGIN_REQUIRED', True)
    brand = getattr(settings, 'FRONTEND_BRAND', 'Django Fast Frontend')
    logo = getattr(settings, 'FRONTEND_LOGO', 'img/django-fast-frontend-logo.png')
    css = getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css')
    description = getattr(settings, 'FRONTEND_DESCRIPTION', '')


if not 'config' in frontend.site._registry:
    frontend.site.register_config(Frontend)

    if getattr(frontend.site._registry['config'].__class__, 'login_required') and getattr(frontend.site._registry['config'].__class__(), 'authentication'):
        frontend.site.register_accounts(AccountFrontend)
