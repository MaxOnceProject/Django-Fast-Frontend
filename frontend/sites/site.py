from django.conf import settings
from django.shortcuts import redirect
from .abstract import FrontendSiteAbstract


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
            raise AttributeError('Please specify an account class')
        self.register(model='accounts', frontend_class=account_class)

    def get_model_config(self, model):
        """
        gets the frontend configuration for the given model.
        """

        return site._registry[model].__class__(model=model)

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