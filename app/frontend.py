import frontend
from app.models import Author


# Register your models here.
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title')
    inline_button = 'check'
    table_add = False
    table_show = True


    def post_inline_button(self, object):
        print(object.name)

frontend.site.register(Author, AuthorFrontend)
