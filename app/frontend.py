from django.http import HttpResponseRedirect

import frontend
from app.models import Author


# Register your models here.
class AuthorFrontend(frontend.ModelFrontend):
    # fields = ('name', 'title')
    list_display = ('name', 'title')
    table_inline_button = ('check', 'uncheck')
    table_add = False
    table_show = True
    cards = False
    # list_filter = ('name', 'title')
    search_fields = ('name', 'title', 'birth_date')
    readonly_fields = ('name', 'title')
    change_permission = True
    delete_permission = True
    add_permission = True
    list_per_page = 100
    toolbar_button = ('everything', 'everything_everything')
    description = f"everything_everything everything_everything everything_everything " \
                   f"everything_everything everything_everything everything_everything " \
                   f"everything_everything everything_everything everything_everything " \
                   f"everything_everything everything_everything everything_everything"
    # show_permission = True

    def everything(self):
        print(self)

    def everything_everything(self):
        print(self)

    def check(self, object):
        print(object.name)

    def uncheck(self, object):
        print(object.title)

    def queryset(self):
        pass

frontend.site.register(Author, AuthorFrontend)
