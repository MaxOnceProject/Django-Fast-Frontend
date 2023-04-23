import frontend
from django.conf import settings
class Frontend(frontend.Config):
    authentication = getattr(settings, 'FRONTEND_AUTHENTICATION', True)


if not 'config' in frontend.site._registry:
    frontend.site.register_config(Frontend)

    if getattr(frontend.site._registry['config'].__class__, 'authentication'):
        frontend.site.register_accounts()
