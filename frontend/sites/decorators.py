def register(models=None, site=None):
    """
    Register the given model(s) classes and wrapped ModelAdmin class with
    admin site:

    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass

    The `site` kwarg is an admin site to use instead of the default admin site.
    """
    from .model import ModelFrontend
    from .site import site

    def _frontend_register_wrapper(frontend_class):

        site.register(models, frontend_class=frontend_class)

        return frontend_class

    return _frontend_register_wrapper