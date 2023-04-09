## Get Started
1. Install Django Fast Frontend in your project:  
`pip install django-fast-frontend`
2. Add Django Fast Frontend and Django Bootstrap 5 to your `INSTALLED_APPS`:
```
INSTALLED_APPS = [
    ...
    'django_fast_frontend',
    'django_bootstrap5'
]
```
2. Create a file called `frontend.py` in one of you Django apps
3. Create a frontend based on one of you models:
```
import frontend
from app.models import Author


# Register your models here.
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title')

frontend.site.register(Author, AuthorFrontend)
```

## Django Models
- Use `verbose_name_plural` and `verbose_name` to display a correct name for your model tables in the frontend
```
class Author(models.Model):
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        db_table_comment = "A List of Authors"
```
## Django URLs
- Django Fast Frontend will automatically add its URLs to the root URL file in your Django project.  
- Important: setting a path in your root URL file to `''` will interfere with other URL paths.
- See options to modify the frontend URL in Django Settings

## Custom CSS Styles
- Add a custom.css to the following path `static/custom.css`
- See options to modify the `static/custom.css` path in Django Settings

## Inline Button
- Add a class property called `inline_button = 'name-of-your-button`
- Add a function called `post_inline_button` to execute a function
```
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title')
    inline_button = 'check'

    def post_inline_button(self, object):
        print(object.name)

frontend.site.register(Author, AuthorFrontend)
```

## Django Settings
- `FRONTEND_URL = 'your-favorite-url-path'`  
_(Note that adding or removing leading or trailing `/` will have no effect on the path creation)_

- `FRONTEND_TITLE = 'Your Page Name'`