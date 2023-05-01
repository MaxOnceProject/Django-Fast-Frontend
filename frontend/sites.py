from abc import ABC
from importlib import import_module
from django.apps import apps
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

from frontend.forms import generate_form_for_model

class FrontendSiteAbstract(ABC):
    pass


class FrontendSite:
    def __init__(self, name="frontend"):
        """
        Initializes a new FrontendSite instance.
        """

        self._registry = {}
        self.name = name
        self.global_config = None
        self.navbar_registry = None
        self.cards = None

    def register(self, model, frontend_class=None):
        """
        Registers a model with the frontend site using the given frontend class.
        """

        if frontend_class is None:
            AttributeError('Please specify a frontend class')
        self._registry[model] = frontend_class()

    def register_config(self, config_class=None):
        """
        Registers a global frontend configuration class.
        """

        if config_class is None:
            raise AttributeError('Please specify a configuration class')
        self.register(model='config', frontend_class=config_class)

    def register_accounts(self, account_class=None):
        """
        Registers an accounts frontend configuration class.
        """

        if account_class is None:
            account_class = AccountFrontend
        self.register(model='accounts', frontend_class=account_class)

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
                    if isinstance(value, ModelFrontend):
                        self.register(value.model, value.__class__)
            except ImportError:
                continue

    def load_global_config(self):
        """
        Loads the global frontend configuration.
        """

        self.global_config = self._registry['config'].__class__
        return  self.global_config

    def load_model_config(self, model):
        """
        Loads the frontend configuration for the given model.
        """

        return site._registry[model].__class__

    def load_navbar_registry(self):
        """
        Loads the navbar registry with models from the registered frontend classes.
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

    def load_navbar_registry_by_app(self, register, app_name):
        """
        Loads the navbar registry filtered by the given app name.
        """

        return {app_name: register[app_name]}

    @property
    def urls(self):
        """
        Returns the urlpatterns and the frontend site namespace.
        """

        from .urls import urlpatterns
        return urlpatterns, "", self.name

    def http_response(self, request, context=None, template=None):
        """
        Returns the urlpatterns and the frontend site namespace.
        """

        if not self.global_config:
            self.load_global_config()

        if not self.navbar_registry:
            self.load_navbar_registry()

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
        return render(request, template, context)

    def http_home_response(self, request, context):
        """
        Handles HTTP response for the model pages.
        """

        return self.http_response(request, context, template="frontend/home.html")

    def http_model_response(self, request, context):
        """
        Handles HTTP response for the model pages.
        """

        return self.http_response(request, context, template="frontend/site.html")

    def http_login_redirect(self, request):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    def load_cards(self):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        if not self.navbar_registry:
            self.load_navbar_registry()
        if getattr(self.global_config, 'authentication', False):
            self.cards = self.navbar_registry.copy()
            del self.cards['accounts']
        else:
            self.cards = self.navbar_registry
        return self.cards

    def generate_form_for_model(self, model, fields):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        return generate_form_for_model(model, fields)

    def load_model_fields(self, model_config):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        return list(getattr(model_config, 'list_display', []))

    def load_model_objects(self, model, fields):
        """
        Loads objects of a model with the specified fields.
        """

        if 'id' in fields:
            objects = model.objects.values(*fields)
        elif not fields:
            objects = model.objects.values()
            if objects.exists():
                fields = [field for field in objects[0].keys() if field != 'id']
            else:
                fields = [field.name for field in model._meta.fields if field.name != 'id']
        else:
            objects = model.objects.values(*fields, 'id')
        return objects, fields

    def load_pagination(self, request, objects, list_per_page):
        """
        Loads a paginator for the objects and returns the paginated objects.
        """

        paginator = Paginator(objects, list_per_page)  # Show x items per page
        objects = paginator.get_page(request.GET.get("page"))
        return objects

    def load_model_actions(self, table_inline_button):
        table_fields = []
        if table_inline_button:
            for action in table_inline_button:
                table_fields += [action]
        return table_fields

    def load_model_filter(self, objects, search_fields, search_query, filter_fields, filter_args, sort_fields, sort_args):
        # Apply search filters
        if search_fields and search_query:
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            objects = objects.filter(query)

        # Apply additional filters from filter_params
        if filter_fields and filter_args:
            query = Q()
            for field in filter_fields:
                if field in filter_args:
                    # query &= Q(**{f"{field}__in": filter_args[field]})
                    for filter_arg in filter_args[field]:
                        query |= Q(**{f"{field}__icontains": filter_arg})
            objects = objects.filter(query)

        # Apply sorting from sort_params
        if sort_fields and sort_args:
            sort_fields = list(sort_fields) + [f'-{field}' for field in sort_fields]
            if sort_args and sort_args in sort_fields:
                objects = objects.order_by(sort_args)

        return objects

    def get_filter_options(self, model, list_filter):
        filter_options = {}
        for field in list_filter:
            filter_field = model._meta.get_field(field)
            filter_options[field] = filter_field.choices if hasattr(filter_field, 'choices') and filter_field.choices else model.objects.values_list(field, flat=True).distinct()
        return filter_options

if getattr(settings, 'FRONTEND_SITE_CLASS', None):
    site = getattr(settings, 'FRONTEND_SITE_CLASS')()
else:
    site = FrontendSite()


class ModelFrontend:
    """
    A class representing a frontend configuration for a Django model.

    :param model: The Django model to configure frontend settings for
    """

    pass


class Config:
    """
    A class representing a generic configuration object.
    """

    authentication = True
    brand = str()
    logo = str()
    css = str()

class AccountFrontend:
    """
    A class representing frontend configuration for user authentication.

    :ivar authentication: A boolean indicating whether authentication is enabled for the frontend
    """

    pass
