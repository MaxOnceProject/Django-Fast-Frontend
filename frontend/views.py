import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from . import site

logger = logging.getLogger(__name__)


def _safe_redirect(request, fallback="/"):
    """
    Returns a safe HttpResponseRedirect. Uses the HTTP_REFERER only if it
    points to the same host; otherwise falls back to *fallback*.
    """
    referer = request.META.get("HTTP_REFERER", "")
    allowed_hosts = {request.get_host()}
    if url_has_allowed_host_and_scheme(referer, allowed_hosts=allowed_hosts):
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(fallback)


def favicon_view(request):
    """
    Handles favicon requests by returning an empty 204 No Content response.

    :param request: Django HttpRequest object
    :return: HttpResponse with status 204
    """
    return HttpResponse(status=204)


class FrontendModelView(TemplateView):
    """
    A generic frontend view that can be used to display models and handle common actions like
    creating, updating, and deleting model instances. This view also handles pagination and searching.
    """

    @staticmethod
    def _check_global_auth(request):
        """
        Centralised global authentication check used by both GET and POST.
        Returns a redirect response if the user must log in, or None if OK.
        """
        global_config = site.get_global_config()
        login_required = getattr(global_config, 'login_required', True)
        authentication = getattr(global_config(), 'authentication', True)
        if login_required and authentication and not request.user.is_authenticated:
            return site.http_login_redirect(request)
        return None

    @staticmethod
    def _check_model_auth(request, model_config):
        """
        Centralised per-model authentication check used by both GET and POST.
        Returns a redirect response if the user must log in, or None if OK.
        """
        global_config = site.get_global_config()
        model_login_required = model_config.get_login_required()
        authentication = getattr(global_config(), 'authentication', True)
        if model_login_required and authentication and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return None

    def get(self, request, *args, app_name=None, model_name=None, action=None, id=None):
        """
        A generic frontend view that can be used to display models and handle common actions like
        creating, updating, and deleting model instances. This view also handles pagination and searching.
        """

        # Centralised global authentication check
        auth_response = self._check_global_auth(request)
        if auth_response:
            return auth_response

        # pre-get navbar
        navbar_registry = site.get_navbar_registry()

        # landing page for website
        if app_name is None:
            cards = site.get_cards()
            return site.http_home_response(
                request,
                context={
                    "meta": {
                        "cards": cards,
                        "title": "Home",
                    },
                })

        # Landing page for app
        if model_name is None:
            return site.http_home_response(
                request,
                context={
                    "meta": {
                        "cards": site.get_navbar_registry_by_app(navbar_registry, app_name),
                        "title": "Home",
                    },
                })

        # get model site config
        model = apps.get_model(app_name, model_name)
        model_config = site.get_model_config(model)

        # Centralised per-model authentication check
        model_auth_response = self._check_model_auth(request, model_config)
        if model_auth_response:
            return model_auth_response

        # create model forms
        form_class = model_config.get_form()
        form = form_class()

        if action in ['table_add', 'table_change', 'table_delete']:

            if id and action in ['table_change'] and model_config.has_change_permission():
                qs = model_config.get_queryset(request)
                object = qs.get(id=id)
                form = form_class(request.POST or None, initial=object.__dict__)
                if model_config.get_readonly_fields():
                    for readonly_field in model_config.get_readonly_fields():
                        form.fields[readonly_field].widget.attrs['readonly'] = True

        list_display = model_config.get_list_display()
        # initiate data object
        objects, table_fields = model_config.queryset(request)

        # get search, filter and sort
        search_fields = model_config.get_search_fields()
        list_filter = model_config.get_list_filter()
        sortable_by = model_config.get_sortable_by()
        list_filter_options = model_config.get_filter_options()

        search_query = request.GET.get("q", "")
        sort_args = request.GET.get("s", "")
        filter_args = model_config.get_filter_args(request.GET)


        # Apply search, filter and sort
        objects = model_config.get_search_results(objects, search_fields, search_query)
        objects = model_config.get_filter_results(objects, list_filter, filter_args)
        objects = model_config.get_sort_results(objects, sortable_by, sort_args)

        # Pagination
        objects = model_config.get_pagination(request, objects)

        inline_button = model_config.get_inline_button()
        table_fields += model_config.get_model_actions(inline_button)

        return site.http_model_response(
            request,
            context={
                "option": {
                    "site": {
                        "title": getattr(model_config, 'title', True),
                        "description": getattr(model_config, 'description', False),
                    },
                    "table": {
                        "toolbar_button": model_config.get_toolbar_button(),
                        "cards": model_config.get_cards(),
                        "show": model_config.has_view_permission(),
                        "add": model_config.has_add_permission(),
                        "change": model_config.has_change_permission(),
                        "delete": model_config.has_delete_permission(),
                        "search": model_config.get_search_fields(),
                        "filter": model_config.get_list_filter(),
                        "sort": model_config.get_sortable_by(),
                        "inline_button": model_config.get_inline_button(),
                    },
                },
                "site": {
                    "title": getattr(model._meta, 'verbose_name_plural',
                                     getattr(model._meta, 'verbose_name', model._meta.model_name)),
                    "description": getattr(model_config, 'description', False),
                },
                "table": {
                    "form": form or None,
                    "objects": objects,
                    "fields": table_fields,
                    "inline_button": inline_button,
                    "toolbar_button": model_config.get_toolbar_button(),
                    "search_query": search_query,
                    "filter_fields": list_filter,
                    "list_filter_options": list_filter_options,
                    "filter_args": filter_args,
                    "sort_fields": sortable_by,
                    "sort_args": sort_args,
                }
            })

    def post(self, request, *args, app_name=None, model_name=None, action=None, id=None):
        """
        Handles POST requests for the FrontendModelView.

        :param request: Django HttpRequest object
        :param args: Additional arguments
        :param app_name: Name of the Django app
        :param model_name: Name of the model
        :param action: The action to be performed (add, change, delete)
        :param id: The ID of the model instance to be modified
        :return: A HttpResponse object with the appropriate response for the request
        """

        # Centralised global authentication check (same as GET)
        auth_response = self._check_global_auth(request)
        if auth_response:
            return auth_response

        # get model site config
        model = apps.get_model(app_name, model_name)
        model_config = site.get_model_config(model)

        # Centralised per-model authentication check (same as GET)
        model_auth_response = self._check_model_auth(request, model_config)
        if model_auth_response:
            return model_auth_response

        # Fallback URL for safe redirects
        fallback_url = f"/{app_name}/{model_name}/"

        # create model forms
        form_class = model_config.get_form()

        if action == 'table_change' and model_config.change_permission:
            qs = model_config.get_queryset(request)
            object = qs.get(id=id)
            form = form_class(request.POST, instance=object)
            if form.is_valid():
                form.save()
            return _safe_redirect(request, fallback=fallback_url)

        if action == 'table_add' and model_config.add_permission:
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
            return _safe_redirect(request, fallback=fallback_url)

        if action == 'table_delete' and model_config.delete_permission:
            qs = model_config.get_queryset(request)
            object = qs.get(id=id)
            object.delete()
            return HttpResponseRedirect(fallback_url)

        # Toolbar button dispatch — validate action is declared AND callable
        toolbar_actions = getattr(model_config, 'toolbar_button', ())
        if action and action in toolbar_actions:
            handler = getattr(model_config, action, None)
            if callable(handler):
                handler()
            else:
                logger.warning(
                    "Action '%s' declared in toolbar_button for %s is not callable.",
                    action, model_config.__class__.__name__,
                )
            return _safe_redirect(request, fallback=fallback_url)

        # Inline button dispatch — validate action is declared AND callable
        inline_actions = getattr(model_config, 'inline_button', ())
        if action and action in inline_actions:
            handler = getattr(model_config, action, None)
            if callable(handler):
                qs = model_config.get_queryset(request)
                object = qs.get(id=id)
                handler(object)
            else:
                logger.warning(
                    "Action '%s' declared in inline_button for %s is not callable.",
                    action, model_config.__class__.__name__,
                )
            return _safe_redirect(request, fallback=fallback_url)

        # No matching action — return to model list
        return HttpResponseRedirect(fallback_url)


class FrontendAbstractView(TemplateView):
    """
    An abstract view that serves as a base for frontend views, providing common context data.
    """

    title = ''

    def get_context_data(self, **kwargs):
        """
        An abstract view that serves as a base for frontend views, providing common context data.
        """

        context = super().get_context_data()
        context = site.get_site_meta(context)
        context['meta']['title'] = self.title
        return context

class FrontendLoginView(auth_views.LoginView, FrontendAbstractView):
    """
    A frontend view for handling user login.
    """

    title = 'Login'

class FrontendLogoutView(auth_views.LogoutView, FrontendAbstractView):
    """
    A frontend view for handling user logout.
    """

    title = 'Logout'

class FrontendPasswordChangeView(FrontendAbstractView, auth_views.PasswordChangeView):
    """
    A frontend view for handling user logout.
    """

    title = 'Password Change'

class FrontendPasswordChangeDoneView(FrontendAbstractView, auth_views.PasswordChangeDoneView):
    """
    A frontend view for handling user logout.
    """

    title = 'Password Change Done'

class FrontendPasswordResetView(FrontendAbstractView, auth_views.PasswordResetView):
    """
    A frontend view for handling user password reset requests.
    """

    title = 'Password Reset'

class FrontendPasswordResetDoneView(FrontendAbstractView, auth_views.PasswordResetDoneView):
    """
    A frontend view for handling user password reset requests.
    """

    title = 'Password Reset Done'

class FrontendPasswordResetConfirmView(FrontendAbstractView, auth_views.PasswordResetConfirmView):
    """
    A frontend view for handling user password reset requests.
    """

    title = 'Password Reset Confirm'

class FrontendPasswordResetCompleteView(FrontendAbstractView, auth_views.PasswordResetCompleteView):
    """
    A frontend view for displaying a confirmation message after a successful password reset.
    """

    title = 'Password Reset Complete'


class FrontendSignUpView(FrontendAbstractView):
    """
    A frontend view for displaying a confirmation message after a successful password reset.
    """

    title = 'Sign Up'

    def get_context_data(self, **kwargs):
        def get_context_data(self, **kwargs):
            """
            Retrieves context data
            :param kwargs: Additional keyword arguments
            :return: A dictionary with the context data
            """
        context = super().get_context_data()
        context['form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for user registration.

        :param request: Django HttpRequest object
        :param args: Additional arguments
        :param kwargs: Additional keyword arguments
        :return: HttpResponseRedirect object to redirect the user to the login redirect URL if registration is successful,
                 otherwise, returns a rendered form with errors
        """

        form = UserCreationForm(self.request.POST)
        if form.is_valid():
            user = form.save()
            login(self.request, user)
            return HttpResponseRedirect(getattr(settings, 'LOGIN_REDIRECT_URL', '/'))
        else:
            context = {'form': form}
            return render(request, "accounts/form.html", context)

