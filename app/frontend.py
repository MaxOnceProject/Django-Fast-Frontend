import frontend
from app.models import Author


# Register your models here.
class AuthorFrontend(frontend.ModelFrontend):
    # fields = ('name', 'title')
    table_inline_button = ('check', 'uncheck')
    table_add = False
    table_show = True
    # list_filter = ('name', 'title')
    search_fields = ('name', 'title')


    def check(self, object):
        print(object.name)

    def uncheck(self, object):
        print(object.title)

    def queryset(self):
        pass

frontend.site.register(Author, AuthorFrontend)
