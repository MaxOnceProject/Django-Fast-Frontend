from django.http import HttpResponseRedirect

import frontend
from app.models import Author

# class Frontend(frontend.Config):
#     authentication = False
#
# frontend.site.register_config(Frontend)

# Register your models here.
class AuthorFrontend(frontend.ModelFrontend):
    # fields = ('name', 'title')
    login_required = False
    list_display = ('name', 'title')
    table_inline_button = ('check', 'uncheck')
    # view_permission = False
    # cards = True
    # list_filter = ('name', 'title')
    search_fields = ('name', 'title', 'birth_date')
    # readonly_fields = ('name', 'title')
    change_permission = True
    # delete_permission = True
    add_permission = True
    list_per_page = 5
    toolbar_button = ('everything', 'everything_everything')
    description = f"everything_everything everything_everything everything_everything "
    #                f"everything_everything everything_everything everything_everything " \
    #                f"everything_everything everything_everything everything_everything " \
    #                f"everything_everything everything_everything everything_everything"
    # list_filter = ('name', 'title', 'birth_date')  # List of fields available for filtering
    # sortable_by = ('name', 'title')  # List of fields available for sorting

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
