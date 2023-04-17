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
    cards = True
    # list_filter = ('name', 'title')
    search_fields = ('name', 'title', 'birth_date')
    readonly_fields = ('name', 'title')
    change_permission = True
    delete_permission = True
    add_permission = True
    list_per_page = 100
    # show_permission = True

    def check(self, object):
        print(object.name)

    def uncheck(self, object):
        print(object.title)

    def queryset(self):
        pass

frontend.site.register(Author, AuthorFrontend)
