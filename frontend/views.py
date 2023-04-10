# frontend_admin/views.py
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django_filters import ChoiceFilter

from .forms import generate_form_for_model
from . import site
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q


def favicon_view(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_filter_class(model, filters):
    Meta = type("Meta", (), {"model": model, "fields": filters})
    filter_class = type(f"{model.__name__}Filter", (django_filters.FilterSet,), {"Meta": Meta})
    return filter_class

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

    form_class = generate_form_for_model(model)

    if request.method == "POST":
        if action in getattr(frontend_config, 'table_inline_button'):
            model = apps.get_model(app_name, model_name)
            frontend_config = site._registry[model].__class__

            object = model.objects.get(id=id)
            getattr(frontend_config(), action)(object)

        if action == 'table_add':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    fields = list(getattr(frontend_config, 'fields', []))

    if 'id' in fields:
        objects = model.objects.values(*fields)
    elif not fields:
        objects = model.objects.values()
    else:
        objects = model.objects.values(*fields, 'id')

    # Search
    search_fields = getattr(frontend_config, 'search_fields', None)
    if search_fields:
        search_query = request.GET.get("q", "")
        frontend_config.search_fields_option = True
        if search_query:
            search_query_list = [Q(**{f"{field}__icontains": search_query}) for field in search_fields]
            objects = objects.filter(Q(*search_query_list, _connector=Q.OR))

    # Pagination
    paginator = Paginator(objects, 10)  # Show x items per page
    page = request.GET.get("page")
    objects = paginator.get_page(page)


    if getattr(frontend_config, 'table_inline_button', False):
        frontend_config.inline_button_option = True
        fields += ['action']

    context = {
        "meta": {
            "navbar": site.create_navbar_register(),
            "title": getattr(model._meta, 'verbose_name_plural', getattr(model._meta, 'verbose_name', model._meta.model_name)),
            "css": getattr(settings, 'FRONTEND_CUSTOM_CSS', 'css/custom.css'),
        },
        "option": {
            "table": {
                "add": False,
                "show": True,
                "search": getattr(frontend_config, 'search_fields_option', False),
                "inline_button": getattr(frontend_config, 'inline_button_option', False),
            },
        },
        "table": {
            "form": form_class(),
            "objects": objects,
            "fields": fields,
            "inline_button": getattr(frontend_config, 'table_inline_button', None),
        }
    }
    return render(request, "frontend/site.html", context)


def post_view(request, app_name=None, model_name=None):
    if request.method == "POST":
        model = apps.get_model(app_name, model_name)
        frontend_config = site._registry[model].__class__


    # form_class = generate_form_for_model(model)
    # if request.method == "POST":
    #     form = form_class(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect(request.path)
    # else:
    #     form = form_class()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))