# frontend_admin/views.py
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import generate_form_for_model
from . import site
from django.apps import apps


def favicon_view(request):
    return {}

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
        if action == 'inline_button':
            model = apps.get_model(app_name, model_name)
            frontend_config = site._registry[model].__class__

            object = model.objects.get(id=id)
            frontend_config().post_inline_button(object)

        if action == 'table_add':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    fields = list(frontend_config.fields)

    if 'id' in frontend_config.fields:
        objects = model.objects.values(*fields)
    else:
        objects = model.objects.values(*fields, 'id')

    if getattr(frontend_config, 'inline_button', False):
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
                "inline_button": getattr(frontend_config, 'inline_button_option', False)
            },
        },
        "table": {
            "form": form_class(),
            "objects": objects,
            "fields": fields,
            "inline_button": getattr(frontend_config, 'inline_button', None),
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