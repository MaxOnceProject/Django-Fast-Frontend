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


def action(function=None, *, description=None):
    """Attach metadata to a frontend action method.

    Mirrors the Django admin action metadata pattern while keeping
    django-fast-frontend's existing string-based action registration.
    """

    def decorator(func):
        if description is not None:
            func.short_description = description
        return func

    if function is None:
        return decorator
    return decorator(function)