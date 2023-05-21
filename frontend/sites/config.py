from django.conf import settings
from django.urls import get_resolver
from .abstract import FrontendAbstract
import logging



class Config(FrontendAbstract):
    """
    A class representing a generic configuration object.
    """

    login_required = True
    brand = str()
    logo = str()
    css = str()
    description = str()

    @property
    def authentication(self):
        if self.login_required and \
           settings.AUTHENTICATION_BACKENDS and \
           'account_login' in get_resolver(None).reverse_dict.keys():
            return True
        else:
            logging.warning('There is no active authentication configuration for your Django Fast Frontend.')
            return False
