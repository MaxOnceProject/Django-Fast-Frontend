# frontend_admin/views.py
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import generate_form_for_model
from . import site
from django.apps import apps


def frontend_view(request, app_name=None, model_name=None):
    register = site.create_navbar_register()
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
    objects = model.objects.values(*frontend_config.fields)
    fields = frontend_config.fields

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path)
    else:
        form = form_class()

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
            },
        },
        "table": {
            "form": form,
            "objects": objects,
            "fields": fields,
        }
    }
    return render(request, "frontend/site.html", context)
