# frontend_admin/views.py
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django_filters import ChoiceFilter

from .forms import generate_form_for_model
from . import site
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q


def favicon_view(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def frontend_view(request, app_name=None, model_name=None, action=None, id=None):
    register = site.create_navbar_register()
    # Landing page for root
    if app_name == 'favicon.ico':
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if app_name is None:
        context = {
            "meta": {
                "navbar": register,
                "cards": register,
                "title": "Home",
                "css": getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css'),
            },
            "option": {
                "table": {
                    "add": False,
                    "show": False,
                }
            },
        }
        return render(request, "frontend/home.html", context)
    # Landing page for app
    if model_name is None:
        context = {
            "meta": {
                "navbar": register,
                "cards": site.create_navbar_register_by_app(register, app_name),
                "title": "Home",
                "css": getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css'),
            },
            "option": {
                "table": {
                    "add": False,
                    "show": False,
                }
            },
        }
        return render(request, "frontend/home.html", context)

    model = apps.get_model(app_name, model_name)
    frontend_config = site._registry[model].__class__

    if getattr(frontend_config, 'toolbar_button', True) and not request.user.is_authenticated:
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
