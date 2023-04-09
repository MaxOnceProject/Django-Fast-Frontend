# from django.utils.module_loading import autodiscover_modules

from .sites import  site, \
                    FrontendSite, \
                    ModelFrontend

# import frontend.urls as urls

# from django.contrib.admin.options import ModelAdmin as ModelFrontend
# from django.contrib.admin.decorators import action, display, register


# def autodiscover():
#     autodiscover_modules("frontend", register_to=site)
