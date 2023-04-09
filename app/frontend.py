import frontend
from app.models import Author


# Register your models here.
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title')

frontend.site.register(Author, AuthorFrontend)
