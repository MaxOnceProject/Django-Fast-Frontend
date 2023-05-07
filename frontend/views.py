from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from . import site


def favicon_view(request):
    """
    Handles favicon requests and redirects the user back to the referring page.

    :param request: Django HttpRequest object
    :return: HttpResponseRedirect object to redirect the user to the referring page
    """
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class FrontendModelView(TemplateView):
    """
    A generic frontend view that can be used to display models and handle common actions like
    creating, updating, and deleting model instances. This view also handles pagination and searching.
    """

    def get(self, request, *args, app_name=None, model_name=None, action=None, id=None):
        """
        A generic frontend view that can be used to display models and handle common actions like
        creating, updating, and deleting model instances. This view also handles pagination and searching.
        """

        # get global site config
        global_config = site.get_global_config()
        global_authentication = getattr(global_config, 'authentication', True)

        # if global authentication is active this validates that the user is authenticated
        if global_authentication and not request.user.is_authenticated:
            return site.http_login_redirect(request)

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
        model_authentication = model_config.get_login_required()

        # if model authentication is active this validates that the user is authenticated
        if model_authentication and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        fields = model_config.get_fields()

        # create model forms
        form_class = model_config.get_form()
        form = form_class()

        if action in ['table_add', 'table_change', 'table_delete']:

            if id and action in ['table_change'] and model_config.has_change_permission():
                object = model.objects.get(id=id)
                form = form_class(request.POST or None, initial=object.__dict__)
                if model_config.get_readonly_fields():
                    for readonly_field in model_config.get_readonly_fields():
                        form.fields[readonly_field].widget.attrs['readonly'] = True

        list_display = model_config.get_list_display()
        # initiate data object
        objects, table_fields = model_config.queryset()

        # get search, filter and sort
        search_fields = model_config.get_search_fields()
        list_filter = model_config.get_list_filter()
        sortable_by = model_config.get_sortable_by()
        list_filter_options = model_config.get_filter_options()

        search_query = request.GET.get("q", "")
        sort_args = request.GET.get("s", "")
        request_dict = dict(request.GET)

        filter_args = {filter: request_dict[filter] for filter in request_dict if filter not in ['q', 's'] and request.GET[filter] != ''}

        # Apply search, filter and sort
        objects = model_config.get_model_filter(objects, search_fields, search_query, list_filter, filter_args, sortable_by, sort_args)

        # Pagination
        list_per_page = model_config.get_list_per_page()
        objects = model_config.get_pagination(request, objects)

        table_inline_button = getattr(model_config, 'table_inline_button', [])
        table_fields += model_config.get_model_actions(table_inline_button)

        return site.http_model_response(
            request,
            context={
                "option": {
                    "site": {
                        "title": getattr(model_config, 'title', True),
                        "description": getattr(model_config, 'description', False),
                    },
                    "table": {
                        "toolbar_button": getattr(model_config, 'toolbar_button', False),
                        "cards": getattr(model_config, 'cards', False),
                        "show": model_config.has_view_permission(),
                        "add": model_config.has_add_permission(),
                        "change": model_config.has_change_permission(),
                        "delete": model_config.has_delete_permission(),
                        "search": model_config.get_search_fields(),
                        "filter": model_config.get_list_filter(),
                        "sort": model_config.get_sortable_by(),
                        "inline_button": getattr(model_config, 'table_inline_button', False),
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
                    "inline_button": table_inline_button,
                    "toolbar_button": getattr(model_config, 'toolbar_button', None),
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

        # get global site config
        global_config = site.get_global_config()
        global_authentication = getattr(global_config, 'authentication', True)

        # if global authentication is active this validates that the user is authenticated
        if global_authentication and not request.user.is_authenticated:
            return site.http_login_redirect(request)

        # get model site config
        model = apps.get_model(app_name, model_name)
        model_config = site.get_model_config(model)
        model_authentication = getattr(model_config, 'login_required', True)

        # if model authentication is active this validates that the user is authenticated
        if model_authentication and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        fields = model_config.get_fields()

        # create model forms
        form_class = model_config.get_form()

        if action == 'table_change' and model_config.change_permission:
            object = model.objects.get(id=id)
            form = form_class(request.POST, instance=object)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if action == 'table_add' and model_config.add_permission:
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if action == 'table_delete' and model_config.delete_permission:
            object = model.objects.get(id=id)
            object.delete()
            return HttpResponseRedirect(f"/{app_name}/{model_name}")

        if action in getattr(model_config, 'toolbar_button'):
            getattr(model_config, action)()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if action in getattr(model_config, 'table_inline_button'):
            object = model.objects.get(id=id)
            getattr(model_config, action)(object)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        context['meta'] = {
            "navbar": site.get_navbar_registry(),
            "title": self.title,
            "css": getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css'),
        }
        return context

class FrontendLoginView(FrontendAbstractView, auth_views.LoginView):
    """
    A frontend view for handling user login.
    """

    title = 'Login'

class FrontendLogoutView(FrontendAbstractView, auth_views.LogoutView):
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

