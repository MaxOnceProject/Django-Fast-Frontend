from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import generate_form_for_model
from . import site
from .sites import Config


def favicon_view(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def frontend_view(request, app_name=None, model_name=None, action=None, id=None):
    global_config = site.load_global_config()

    if getattr(global_config, 'authentication', True) and not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    register = site.load_navbar_register()
    if global_config.authentication:
        cards = register.copy()
        del cards['accounts']
    else:
        cards = register

    if app_name is None:
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
                    "cards": site.create_navbar_register_by_app(register, app_name),
                    "title": "Home",
                },
            })


    model = apps.get_model(app_name, model_name)
    frontend_config = site._registry[model].__class__

    if getattr(frontend_config, 'login_required', True) and not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    fields = list(getattr(frontend_config, 'fields', []))
    form_class = generate_form_for_model(model, fields)
    form = form_class()

    if request.method == "POST":
        if action in getattr(frontend_config, 'toolbar_button'):
            getattr(frontend_config(), action)()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        if action in getattr(frontend_config, 'table_inline_button'):
            object = model.objects.get(id=id)
            getattr(frontend_config(), action)(object)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        if action == 'table_change' and frontend_config.change_permission:
            object = model.objects.get(id=id)
            form = form_class(request.POST, instance=object)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        if action == 'table_add' and frontend_config.add_permission:
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        if action == 'table_delete' and frontend_config.delete_permission:
            object = model.objects.get(id=id)
            object.delete()
            return HttpResponseRedirect(f"/{app_name}/{model_name}")

    if id and action in ['table_change'] and frontend_config.change_permission:
        object = model.objects.get(id=id)
        form = form_class(request.POST or None, initial=object.__dict__)
        if frontend_config.readonly_fields:
            for readonly_fields in frontend_config.readonly_fields:
                form.fields[readonly_fields].widget.attrs['readonly'] = True

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


    # Search
    search_fields = getattr(frontend_config, 'search_fields', None)
    search_query = request.GET.get("q", "")
    if search_fields:
        frontend_config.search_fields_option = True
        if search_query:
            search_query_list = [Q(**{f"{field}__icontains": search_query}) for field in search_fields]
            objects = objects.filter(Q(*search_query_list, _connector=Q.OR))

    # Pagination
    paginator = Paginator(objects, getattr(frontend_config, 'list_per_page', 100))  # Show x items per page
    page = request.GET.get("page")
    objects = paginator.get_page(page)

    table_inline_button = getattr(frontend_config, 'table_inline_button', [])

    if table_inline_button:
        frontend_config.inline_button_option = True
        for action in table_inline_button:
            fields += [action]

    context = {
        "meta": {
            "navbar": site.create_navbar_register(),
            "title": getattr(model._meta, 'verbose_name_plural', getattr(model._meta, 'verbose_name', model._meta.model_name)),
            "css": getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css'),
        },
        "option": {
            "site": {
                "title": True,
                "description": getattr(frontend_config, 'description', False),
            },
            "table": {
                "toolbar_button": getattr(frontend_config, 'toolbar_button', False),
                "cards": getattr(frontend_config, 'cards', False),
                "show": getattr(frontend_config, 'table_show', True),
                "add": getattr(frontend_config, 'add_permission', False),
                "change": getattr(frontend_config, 'change_permission', False),
                "search": getattr(frontend_config, 'search_fields_option', False),
                "inline_button": getattr(frontend_config, 'inline_button_option', False),
            },
        },
        "site": {
            "description": getattr(frontend_config, 'description', False),
        },
        "table": {
            "form": form,
            "objects": objects,
            "fields": fields,
            "inline_button": getattr(frontend_config, 'table_inline_button', None),
            "toolbar_button": getattr(frontend_config, 'toolbar_button', None),
            "search_query": search_query
        }
    }
    return render(request, "frontend/site.html", context)

class FrontendAbstractView(TemplateView):
    title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['meta'] = {
            "navbar": site.create_navbar_register(),
            "title": self.title,
            "css": getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css'),
        }
        return context

class FrontendLoginView(FrontendAbstractView, auth_views.LoginView):
    title = 'Login'

class FrontendLogoutView(FrontendAbstractView, auth_views.LogoutView):
    title = 'Logout'

class FrontendPasswordChangeView(FrontendAbstractView, auth_views.PasswordChangeView):
    title = 'Password Change'

class FrontendPasswordChangeDoneView(FrontendAbstractView, auth_views.PasswordChangeDoneView):
    title = 'Password Change Done'

class FrontendPasswordResetView(FrontendAbstractView, auth_views.PasswordResetView):
    title = 'Password Reset'

class FrontendPasswordResetDoneView(FrontendAbstractView, auth_views.PasswordResetDoneView):
    title = 'Password Reset Done'

class FrontendPasswordResetConfirmView(FrontendAbstractView, auth_views.PasswordResetConfirmView):
    title = 'Password Reset Confirm'

class FrontendPasswordResetCompleteView(FrontendAbstractView, auth_views.PasswordResetCompleteView):
    title = 'Password Reset Complete'


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect


class FrontendSignUpView(FrontendAbstractView):
    title = 'Sign Up'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(self.request.POST)
        if form.is_valid():
            user = form.save()
            login(self.request, user)
            return HttpResponseRedirect(getattr(settings, 'LOGIN_REDIRECT_URL', '/'))
        else:
            context = {'form': form}
            return render(request, "accounts/form.html", context)

