from abc import ABC
from importlib import import_module
from django.apps import apps
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from frontend.forms import generate_form_for_model


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

        from .urls import urlpatterns
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
                    if isinstance(value, ModelFrontend):
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


    def http_response(self, request, context=None, template=None):
        """
        Returns the urlpatterns and the frontend site namespace.
        """

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
        return render(request, template, context)



class FrontendSite(FrontendSiteAbstract):

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

    def get_model_config(self, model):
        """
        gets the frontend configuration for the given model.
        """

        return site._registry[model].__class__()

    def get_navbar_registry_by_app(self, register, app_name):
        """
        gets the navbar registry filtered by the given app name.
        """

        return {app_name: register[app_name]}

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

    def get_cards(self):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        if not self.navbar_registry:
            self.get_navbar_registry()
        if getattr(self.global_config, 'authentication', False):
            self.cards = self.navbar_registry.copy()
            del self.cards['accounts']
        else:
            self.cards = self.navbar_registry
        return self.cards


if getattr(settings, 'FRONTEND_SITE_CLASS', None):
    site = getattr(settings, 'FRONTEND_SITE_CLASS')()
else:
    site = FrontendSite()


class ModelFrontend:
    """
    A class representing a frontend configuration for a Django model.

    :param model: The Django model to configure frontend settings for
    """

    # login
    login_required = True

    # toolbar
    toolbar_button = tuple()
    description = str()

    # table
    list_display = tuple()
    cards = False
    list_per_page = 100
    view_permission = True
    table_inline_button = tuple()

    # table search, sort and filter
    search_fields = tuple()
    sortable_by = tuple()  # List of fields available for sorting
    list_filter = tuple()  # List of fields available for filtering

    # form
    fields = list_display  # follows list_display by default
    readonly_fields = tuple()
    change_permission = False
    delete_permission = False
    add_permission = False

    @property
    def actions(self):
        raise NotImplementedError('Use option table_inline_button or toolbar_button.')

    @property
    def actions_on_top(self):
        return NotImplementedError('Use option table_inline_button or toolbar_button.')

    @property
    def actions_on_bottom(self):
        return NotImplementedError('Use option table_inline_button or toolbar_button.')

    @property
    def empty_value_display(self):
        raise NotImplementedError

    @property
    def ordering(self):
        raise NotImplementedError('Use option sortable_by.')

    @property
    def preserve_filters(self):
        raise NotImplementedError

    @property
    def search_help_text(self):
        raise NotImplementedError

    @property
    def show_full_result_count(self):
        raise NotImplementedError

    @property
    def form(self):
        raise NotImplementedError

    @property
    def autocomplete_fields(self):
        raise NotImplementedError

    @property
    def list_select_related(self):
        raise NotImplementedError

    @property
    def formfield_overrides(self):
        raise NotImplementedError

    @property
    def delete_selected_confirmation_template(self):
        raise NotImplementedError

    @property
    def delete_confirmation_template(self):
        raise NotImplementedError

    @property
    def change_list_template(self):
        raise NotImplementedError

    @property
    def change_form_template(self):
        raise NotImplementedError

    @property
    def add_form_template(self):
        raise NotImplementedError

    @property
    def actions_selection_counter(self):
        raise NotImplementedError

    @property
    def date_hierarchy(self):
        raise NotImplementedError('Use option search_fields.')

    @property
    def exclude(self):
        raise NotImplementedError('Use option fields to specify fields to display in form.')

    @property
    def fieldsets(self):
        raise NotImplementedError('Used in Django to cover complex edge case functionality.')

    @property
    def filter_horizontal(self):
        raise NotImplementedError('Use option search_fields.')

    @property
    def filter_vertical(self):
        raise NotImplementedError('Use option search_fields.')

    @property
    def inlines(self):
        raise NotImplementedError('Adding more Information to the Page will bloat the frontend.')

    @property
    def list_display_links(self):
        raise NotImplementedError('An Edit Button will be in place if editing the table row is allowed.')

    @property
    def list_editable(self):
        raise NotImplementedError('Use option readonly_fields.')

    @property
    def paginator(self):
        raise NotImplementedError('Used in Django to cover edge cases.')

    @property
    def prepopulated_fields(self):
        raise NotImplementedError('Use a custom frontend page and use java script or add a custom model form.')

    @property
    def radio_fields(self):
        raise NotImplementedError('Use a custom model form.')

    @property
    def raw_id_fields(self):
        raise NotImplementedError

    @property
    def save_as(self):
        raise NotImplementedError

    @property
    def save_as_continue(self):
        raise NotImplementedError

    @property
    def save_on_top(self):
        raise NotImplementedError

    @property
    def view_on_site(self):
        raise NotImplementedError

    def get_readonly_fields(self):
        return self.readonly_fields

    def get_list_display(self):
        return self.list_display

    def get_fields(self):
        return self.fields

    def has_view_permission(self):
        return self.view_permission

    def has_add_permission(self):
        return self.add_permission

    def has_change_permission(self):
        return self.change_permission

    def has_delete_permission(self):
        return self.delete_permission

    def get_form(self, model, fields):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        return generate_form_for_model(model, fields)

    def get_model_objects(self, model, fields):
        """
        gets objects of a model with the specified fields.
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
        return objects, list(fields)

    def get_pagination(self, request, objects, list_per_page):
        """
        gets a paginator for the objects and returns the paginated objects.
        """

        paginator = Paginator(objects, list_per_page)  # Show x items per page
        objects = paginator.get_page(request.GET.get("page"))
        return objects

    def get_model_actions(self, table_inline_button):
        table_fields = []
        if table_inline_button:
            for action in table_inline_button:
                table_fields += [action]
        return list(table_fields)

    def get_model_filter(self, objects, search_fields, search_query, filter_fields, filter_args, sort_fields, sort_args):
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

    def get_autocomplete_fields(self):
        raise NotImplementedError


class Config:
    """
    A class representing a generic configuration object.
    """

    authentication = True
    brand = str()
    logo = str()
    css = str()
    description = str()


class AccountFrontend:
    """
    A class representing frontend configuration for user authentication.

    :ivar authentication: A boolean indicating whether authentication is enabled for the frontend
    """

    pass
