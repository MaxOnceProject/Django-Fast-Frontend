from importlib import import_module
from django.apps import apps

class FrontendSite:
    def __init__(self, name="frontend"):
        self._registry = {}
        self.name = name

    def register(self, model, frontend_class=None):
        if frontend_class is None:
            frontend_class = ModelFrontend
        self._registry[model] = frontend_class()

    def unregister(self, model):
        del self._registry[model]

    def autodiscover_modules(self):
        for app_config in apps.get_app_configs():
            try:
                frontend_module = import_module(f"{app_config.name}.frontend")
                for key, value in frontend_module.__dict__.items():
                    if isinstance(value, ModelFrontend):
                        self.register(value.model, value.__class__)
            except ImportError:
                continue

    def create_navbar_register(self):
        register = {}

        for model in self._registry.keys():
            app_name = model._meta.app_config.name
            app_verbose_name = getattr(model._meta.app_config, 'verbose_name', model._meta.app_label)
            model_name = model._meta.model_name
            model_verbose__name = getattr(model._meta, 'verbose_name_plural', getattr(model._meta, 'verbose_name', model._meta.model_name))
            model_description = getattr(model._meta, 'db_table_comment', '')
            if not app_name in register:
                register[app_name] = {'verbose_name': app_verbose_name,
                                 'models': []}
            register[app_name]['models'] += [{'name': model_name,
                                            'verbose_name': model_verbose__name,
                                            'description': model_description}]
        return register

    def create_navbar_register_by_app(self, register, app_name):
        return {app_name: register[app_name]}

    @property
    def urls(self):
        from .urls import urlpatterns
        return urlpatterns, "", self.name


site = FrontendSite()


class ModelFrontend:
    def __init__(self, model=None):
        self.model = model
        self.fields = "__all__"
