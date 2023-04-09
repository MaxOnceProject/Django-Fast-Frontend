import importlib

from django.apps import AppConfig
from django.conf import settings
from django.urls import include, path
from django.apps import apps

import frontend.sites


class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'

    default = True

    def ready(self):
        super().ready()

        # autodiscover frontend.py in installed apps
        frontend.site.autodiscover_modules()

        # add frontend urlpatterns
        def get_frontend_url():
            frontend_url = getattr(settings, 'FRONTEND_URL', '')
            if not frontend_url == '':
                if not frontend_url[-1] == '/':
                    frontend_url += '/'
                if frontend_url[0] == '/':
                    frontend_url = frontend_url[1:]
            return frontend_url

        # urlpatterns = []
        # urlpatterns = getattr(importlib.import_module(settings.ROOT_URLCONF), 'urlpatterns', urlpatterns)
        urlpatterns = importlib.import_module(settings.ROOT_URLCONF).urlpatterns
        urlpatterns += [path(get_frontend_url(), include('frontend.urls')),]
        print(urlpatterns)

        # validate
        # add_or_get_installed_app('django_bootstrap5')
        # frontend_apps = getattr(settings, 'FRONTEND_APPS', None)
        # if frontend_apps:
        #     if 'rules' in settings.FRONTEND_APPS:
        #         add_or_get_installed_app('rules')
        #     if 'allauth' in settings.FRONTEND_APPS:
        #         add_or_get_installed_app('allauth')