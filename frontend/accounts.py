from importlib import import_module
from django.apps import apps

class AccountSite:
    def __init__(self, name="accounts"):
        self.name = name

    @property
    def urls(self):
        from .urls import urlpatterns_account
        return urlpatterns_account, "", self.name


site = AccountSite()
