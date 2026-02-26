import logging
from abc import ABC
from importlib import import_module
from django.apps import apps
from django.db import models
from django.shortcuts import render

logger = logging.getLogger(__name__)


def _resolve_model_identifier(identifier):
    """
    Normalize a model identifier to a Django model class.

    Accepts:
    - A Django model class (returned as-is).
    - A string in the form "app_label.ModelName" (resolved via Django app registry).

    Returns the model class, or None if resolution fails.
    """
    if isinstance(identifier, type) and issubclass(identifier, models.Model):
        return identifier
    if isinstance(identifier, str):
        if '.' not in identifier:
            logger.warning("Sidebar: malformed model identifier '%s' (expected 'app_label.ModelName').", identifier)
            return None
        app_label, model_name = identifier.split('.', 1)
        try:
            return apps.get_model(app_label, model_name)
        except (LookupError, ValueError):
            logger.warning("Sidebar: could not resolve model identifier '%s'.", identifier)
            return None
    logger.warning("Sidebar: unsupported model identifier type: %s.", type(identifier))
    return None

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
        self._sidebar_navigation = None

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
            raise AttributeError('Please specify a frontend class')
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

    def set_sidebar_navigation(self, structure):
        """
        Set the site-level sidebar navigation structure.

        Args:
            structure: An ordered dict mapping group display names to
                       lists of model identifiers (classes or
                       "app_label.ModelName" strings).

        Raises:
            TypeError: If structure is not a dict.
        """
        if not isinstance(structure, dict):
            raise TypeError(
                "set_sidebar_navigation() expects a dict mapping group names "
                f"to lists of model identifiers, got {type(structure).__name__}."
            )
        self._sidebar_navigation = structure

    def get_sidebar_registry(self, request=None):
        """
        Build and return the sidebar as an ordered list of groups.

        Each group is a dict: {"group": str, "items": [{"name": ..., "verbose_name": ..., "app_name": ..., "description": ...}, ...]}

        When `_sidebar_navigation` is configured:
        - Only listed models appear (hide-unlisted).
        - Account links are auto-appended if accounts are registered.
        When `_sidebar_navigation` is None:
        - Falls back to app-based grouping from the registry.
        """
        # Auth-aware filtering: hide model links from anonymous users when auth is required
        hide_models = False
        if request is not None:
            if not self.global_config:
                self.get_global_config()
            login_required = getattr(self.global_config, 'login_required', True)
            authentication = getattr(self.global_config(), 'authentication', False)
            if login_required and authentication and not getattr(request.user, 'is_authenticated', False):
                hide_models = True

        sidebar = []

        if not hide_models:
            if self._sidebar_navigation is not None:
                # Configured mode: respect group order, hide unlisted
                for group_name, identifiers in self._sidebar_navigation.items():
                    items = []
                    for identifier in identifiers:
                        model = _resolve_model_identifier(identifier)
                        if model is None:
                            continue
                        if model not in self._registry:
                            logger.warning("Sidebar: model %s is not registered; skipping.", model)
                            continue
                        app_name = model._meta.app_config.name
                        model_name = model._meta.model_name
                        verbose_name = getattr(model._meta, 'verbose_name_plural',
                                               getattr(model._meta, 'verbose_name', model_name))
                        description = getattr(model._meta, 'db_table_comment', '')
                        items.append({
                            'name': model_name,
                            'verbose_name': verbose_name,
                            'app_name': app_name,
                            'description': description,
                        })
                    if items:
                        sidebar.append({'group': group_name, 'items': items})
            else:
                # Fallback mode: derive groups from the registry (app-based)
                app_groups = {}
                for model in self._registry.keys():
                    if model in ('config', 'accounts'):
                        continue
                    app_name = model._meta.app_config.name
                    app_verbose_name = getattr(model._meta.app_config, 'verbose_name', model._meta.app_label)
                    model_name = model._meta.model_name
                    verbose_name = getattr(model._meta, 'verbose_name_plural',
                                           getattr(model._meta, 'verbose_name', model_name))
                    description = getattr(model._meta, 'db_table_comment', '')
                    if app_name not in app_groups:
                        app_groups[app_name] = {'group': app_verbose_name, 'items': []}
                    app_groups[app_name]['items'].append({
                        'name': model_name,
                        'verbose_name': verbose_name,
                        'app_name': app_name,
                        'description': description,
                    })
                sidebar.extend(app_groups.values())

        # Auto-append account links when accounts are registered
        if 'accounts' in self._registry:
            sidebar.append({
                'group': 'Account',
                'items': [
                    {'name': 'login', 'verbose_name': 'Login', 'description': 'Login', 'url_name': 'account_login'},
                    {'name': 'signup', 'verbose_name': 'Sign Up', 'description': 'Sign Up', 'url_name': 'account_signup'},
                    {'name': 'password_change', 'verbose_name': 'Change Password', 'description': 'Change Password', 'url_name': 'account_password_change'},
                ],
            })

        return sidebar

    def get_site_meta(self, context=None, request=None):
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
        # Sidebar is rebuilt per-request (intentional: auth state affects visibility)
        if 'sidebar' not in context['meta']:
            context['meta']['sidebar'] = self.get_sidebar_registry(request=request)
        return context

    def http_response(self, request, context=None, template=None):
        """
        Returns the urlpatterns and the frontend site namespace.
        """
        context = self.get_site_meta(context, request=request)

        return render(request, template, context)