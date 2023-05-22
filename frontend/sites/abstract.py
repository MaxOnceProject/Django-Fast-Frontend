from abc import ABC
from importlib import import_module
from django.apps import apps
from django.shortcuts import render

class FrontendAbstract(ABC):
    pass

class FrontendSiteAbstract(ABC):
    def __init__(self, name="frontend"):
        """
        Initializes a new FrontendSite instance.
        """

        self._registry = {}
        self.name = name
        self.global_config = None
        self.navbar_registry = None
        self.cards = None

    @property
    def urls(self):
        """
        Returns the urlpatterns and the frontend site namespace.
        """

        from ..urls import urlpatterns
        return urlpatterns, "", self.name

    def register(self, model, frontend_class=None):
        """
        Registers a model with the frontend site using the given frontend class.
        """

        if frontend_class is None:
            AttributeError('Please specify a frontend class')
        self._registry[model] = frontend_class()

    def unregister(self, model):
        """
        Registers a model with the frontend site using the given frontend class.
        """

        del self._registry[model]

    def autodiscover_modules(self):
        """
        Registers a model with the frontend site using the given frontend class.
        """

        for app_config in apps.get_app_configs():
            try:
                frontend_module = import_module(f"{app_config.name}.frontend")
                for key, value in frontend_module.__dict__.items():
                    if isinstance(value, FrontendAbstract):
                        self.register(value.model, value.__class__)
            except ImportError:
                continue

    def get_global_config(self):
        """
        gets the global frontend configuration.
        """

        self.global_config = self._registry['config'].__class__
        return  self.global_config


    def get_navbar_registry(self):
        """
        gets the navbar registry with models from the registered frontend classes.
        """

        self.navbar_registry = {}
        for model in self._registry.keys():
            if model == 'config':
                continue
            if model == 'accounts':
                self.navbar_registry['accounts'] = {'verbose_name': 'Account',
                                      'models': []}
                self.navbar_registry['accounts']['models'] += [{'name': 'login',
                                                  'verbose_name': 'Login',
                                                  'description': 'Login'},
                                                   {'name': 'signup',
                                                    'verbose_name': 'Sign Up',
                                                    'description': 'Sign Up'},
                                                   {'name': 'password_change',
                                                    'verbose_name': 'Change Password',
                                                    'description': 'Change Password'},]
                continue
            app_name = model._meta.app_config.name
            app_verbose_name = getattr(model._meta.app_config, 'verbose_name', model._meta.app_label)
            model_name = model._meta.model_name
            model_verbose__name = getattr(model._meta, 'verbose_name_plural', getattr(model._meta, 'verbose_name', model._meta.model_name))
            model_description = getattr(model._meta, 'db_table_comment', '')
            if not app_name in self.navbar_registry:
                self.navbar_registry[app_name] = {'verbose_name': app_verbose_name,
                                 'models': []}
            self.navbar_registry[app_name]['models'] += [{'name': model_name,
                                            'verbose_name': model_verbose__name,
                                            'description': model_description}]
        return self.navbar_registry

    def get_site_meta(self, context=None):
        if not self.global_config:
            self.get_global_config()

        if not self.navbar_registry:
            self.get_navbar_registry()

        if not 'meta' in context:
            context['meta'] = {}
        if not 'navbar' in context['meta']:
            context['meta']['navbar'] = self.navbar_registry
        if not 'css' in context['meta']:
            context['meta']['css'] = getattr(self.global_config, 'css', 'css/custom.css')
        if not 'brand' in context['meta']:
            context['meta']['brand'] = getattr(self.global_config, 'brand', 'Django Fast Frontend')
        if not 'logo' in context['meta']:
            context['meta']['logo'] = getattr(self.global_config, 'logo', 'img/django-fast-frontend-logo.png')
        return context

    def http_response(self, request, context=None, template=None):
        """
        Returns the urlpatterns and the frontend site namespace.
        """
        context = self.get_site_meta(context)

        return render(request, template, context)