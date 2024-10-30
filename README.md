# Django Fast Frontend 
### *Turbocharge Front-End Creation with Django-Admin-Like Configuration*
## Overview
Django Fast Frontend is a Django app that provides an efficient way to customize frontend settings for your Django models. It provides a ``ModelFrontend`` class which allows you to specify various frontend configurations for your models.  
  
_Note: Django Fast Frontend is a complementary package to Django´s powerful MVT based frontend feature. If you require e.g. static pages for your website you can easily add them to your project using the original Django frontend feature._

## Installation
Install Django Fast Frontend with pip:
``` bash
pip install django-fast-frontend
```

Then add ``frontend`` to your ``INSTALLED_APPS`` in your Django project settings:

```python
INSTALLED_APPS = [
    # ...
    'django_bootstrap5',
    'frontend',
    # ...
]
```

## Quick Start
- Add Django Fast Frontend urls to your Django projects ``urls.py``:
````python
from django.urls import path
import frontend

urlpatterns = [
    # ...
    path('', frontend.site.urls),
    # ...
]

````
- Create a file called ``frontend.py`` in one of your Django apps.
- Add a model to your frontend:
```python
import frontend
from app.models import <your-model>


# Register your model here.
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    pass
```
This will create the following features by default:
- A responsive frontend website
- A navigation bar
- A general landing page in your frontend
- A landing page for each Django app in your frontend
- A site with a table containing all fields and data of the Django model registered with Django Fast Frontend in ``frontend.py``


- Setup authentication for sites generated by Django Fast Frontend:
````python
from django.urls import path
import frontend

urlpatterns = [
    # ...
    path('accounts/', frontend.accounts.urls),
    path('', frontend.site.urls),
    # ...
]
````


________________________


# Django Fast Frontend: Documentation
## Configuration
### Project Settings
In your ``settings.py`` file, you can set various global settings for Django Fast Frontend:

```python
# settings.py
# ...

FRONTEND_CUSTOM_CSS = 'css/custom.css'  # Path to custom CSS file
FRONTEND_BRAND = 'Fast Frontend'  # Brand name
FRONTEND_LOGO = 'img/django-fast-frontend-logo-text.PNG'  # Logo file path
FRONTEND_DESCRIPTION = "Powerful and interesting description for your frontend"  # Description for your frontend
FRONTEND_AUTHENTICATION = True  # Whether authentication is required in general

# ...
```

### URL Configuration
In your ``urls.py`` file, include the Django Fast Frontend URLs:

```python
# urls.py
# ...

from django.urls import include, path
import frontend

urlpatterns = [
    # ...
    path('accounts/', include(frontend.accounts.urls)),
    path('', include(frontend.site.urls)),
    # ...
]
```

## Usage
### Django Models
- Use `verbose_name_plural` and `verbose_name` to display a correct name for your model tables in the frontend
```
class Author(models.Model):
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        db_table_comment = "A List of Authors"
```

### Creating a Model Frontend
To create a frontend for a model, you need to create a subclass of 
- ``frontend.ModelFrontend`` and register it with 
- ``frontend.site``. Here's an example for a model named 
- ``Author``:

```python
# app/frontend.py
# ...

import frontend
from app.models import Author

class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title')  # Fields to display
    login_required = False  # Whether login is required
    list_display = ('name', 'title')  # Fields to display in list view
    inline_button = ('inline_button1', 'inline_button2')  # Methods for inline buttons
    view_permission = False  # Whether view permission is required
    cards = True  # Whether to display instances as cards
    list_filter = ('name', 'title')  # Fields for list view filter
    search_fields = ('name', 'title', 'birth_date')  # Fields for search
    readonly_fields = ('name', 'title')  # Fields that are read-only
    change_permission = True  # Whether change permission is required
    delete_permission = True  # Whether delete permission is required
    add_permission = True  # Whether add permission is required
    list_per_page = 5  # Number of instances per page
    toolbar_button = ('toolbar_button1', 'toolbar_button2')  # Methods for toolbar buttons
    description = "Everything about authors."  # Description for the frontend
    sortable_by = ('name', 'title')  # Fields that can be sorted

    # Define your custom methods here:
    def toolbar_button1(self):
        # Your custom code here...

    def toolbar_button2(self):
        # Your custom code here...

    def inline_button1(self, object):
        # Your custom code here...

    def inline_button2(self, object):
        # Your custom code here...

# Register your model frontend:
frontend.site.register(Author, AuthorFrontend)
```

## Customizing the Frontend
You can customize the appearance and behavior of your model frontend by overriding various attributes and methods in your ``ModelFrontend`` subclass.

### Field Display
To customize which fields are displayed in the list view, set ``list_display`` to a tuple of field names:

```python
list_display = tuple()
```

### Field Filtering
To add a filter sidebar that lets users filter the list view by certain fields, set ``list_filter`` to a tuple of field names:

```python
list_filter = tuple()
```

### Field Searching
To enable a search box that lets users search the list view by certain fields, set ``search_fields`` to a tuple of field names:

```python
search_fields = tuple()
```

### Field Sorting
To enable sorting of the list view by certain fields, set ``sortable_by`` to a tuple of field names:

```python
sortable_by = tuple()
```

### Pagination
To customize the number of instances displayed per page, set ``list_per_page`` to the desired number:

```python
list_per_page = 100
```

### Read-Only Fields
To make certain fields read-only in the frontend, set ``readonly_fields`` to a tuple of field names:

```python
readonly_fields = tuple()
```

### Inline Buttons
You can add custom inline buttons to your list view by defining methods for them in your ``ModelFrontend`` subclass and adding them to the ``inline_button`` attribute:

```python
inline_button = ('inline_button1', 'inline_button2')

def inline_button1(self, object):
    # Your custom code here...

def inline_button2(self, object):
    # Your custom code here...
```
_Note: The name of a buttons follows the name of the function._

### Toolbar Buttons
Similarly, you can add custom toolbar buttons by defining methods for them and adding them to the ``toolbar_button`` attribute:

```python
toolbar_button = ('toolbar_button1', 'toolbar_button2')

def toolbar_button1(self):
    # Your custom code here...

def toolbar_button2(self):
    # Your custom code here...
```
_Note: The name of a buttons follows the name of the function._

### Permissions
You can control permissions for viewing, adding, changing, and deleting instances by setting the ``view_permission``, ``add_permission``, ``change_permission``, and ``delete_permission`` attributes:

```python
view_permission = True
change_permission = False
delete_permission = False
add_permission = False
```
Note that these permissions are checked in addition to the standard Django model permissions.

### Description
You can add a description for your model frontend by setting the ``description`` attribute:

```python
description = str()
```
This description will be displayed in the frontend.

### Registration
Finally, to make your model frontend active, you need to register it with ``frontend.site``:

```python
frontend.site.register(Author, AuthorFrontend)
```
This will create URLs for the list, add, change, and delete views for your model, based on the model's name.

## Custom CSS
You can provide a custom CSS file for your Django Fast Frontend by setting ``FRONTEND_CUSTOM_CSS`` in your Django project settings to the path of your CSS file:

```python
FRONTEND_CUSTOM_CSS = 'css/custom.css'
```
This CSS file will be included in all Django Fast Frontend pages.

## Branding
You can specify a custom brand name and logo for your Django Fast Frontend by setting ``FRONTEND_BRAND`` and ``FRONTEND_LOGO`` in your Django project settings:

```python
FRONTEND_BRAND = 'Fast Frontend'
FRONTEND_LOGO = 'img/django-fast-frontend-logo-text.PNG'
```
This brand name and logo will be displayed in the navbar of all Django Fast Frontend pages.  

You can provide a description for your Django Fast Frontend by setting ``FRONTEND_DESCRIPTION`` in your Django project settings:

```python
FRONTEND_DESCRIPTION = "This is a description for the Django Fast Frontend."
```
This description will be displayed on the frontend's main page.

## Frontend URL
By default, Django Fast Frontend automatically generates URLs for your model frontends based on their names. If you want to override this, you can set ``FRONTEND_URL`` in your Django project settings to your desired URL path:

```python
FRONTEND_URL = '/your-favorite-url-path/'
```
Note that this URL path should start and end with a slash.

## Authentication
By default, Django Fast Frontend does not require users to be logged in to view your model frontends. If you want to require login, you can set ``FRONTEND_AUTHENTICATION`` to True in your Django project settings:

```python
FRONTEND_AUTHENTICATION = True
```
Note that this requires Django's authentication system to be properly configured.

Important: To use Django Fast Frontend authentication for sites enable the frontend URLs:
````python
from django.urls import path
import frontend

urlpatterns = [
    # ...
    path('accounts/', frontend.accounts.urls),
    path('', frontend.site.urls),
    # ...
]
````
_Note: It is possible to use a different authentication system._  

In addition, you can customize the URL users are redirected to after login and logout by setting ``LOGIN_REDIRECT_URL`` and ``LOGOUT_REDIRECT_URL`` in your Django project settings:

```python
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

## Integrating with Django's URL System
To integrate Django Fast Frontend with Django's URL system, you need to include its URLs in your Django project's URL configuration.

For example, if you want to serve your Django Fast Frontend at the URL path ``/accounts/``, you can add the following line to your ``urls.py`` file:

```python
path('accounts/', include(frontend.accounts.urls)),
```
Similarly, if you want to serve your Django Fast Frontend at the root URL path /, you can add the following line:

```python
path('', include(frontend.site.urls)),
```

## Customizing the Model Frontend
Django Fast Frontend provides a class-based system for customizing the frontend for each Django model. To create a frontend for a model, you need to create a subclass of ``frontend.ModelFrontend`` and register it with ``frontend.site``.

Here is an example of how to create and register a frontend for the ``Author`` model:

```python
import frontend
from app.models import Author

class AuthorFrontend(frontend.ModelFrontend):
    # ...

frontend.site.register(Author, AuthorFrontend)
```

### Customizing Fields
You can specify which fields of the model to display in the frontend by setting the ``fields`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title')
```

In this example, only the ``name`` and ``title`` fields of the ``Author`` model will be displayed.

### Customizing Permissions
You can control whether users are allowed to view, add, change, or delete objects of the model by setting the ``view_permission``, ``add_permission``, ``change_permission``, and ``delete_permission`` attributes, respectively:

```python
class AuthorFrontend(frontend.ModelFrontend):
    view_permission = False
    change_permission = True
    delete_permission = True
    add_permission = True
```
In this example, users are not allowed to view Author objects, but they are allowed to add, change, and delete them.

### Customizing Display
You can customize how objects of the model are displayed in the list view by setting the ``list_display`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    list_display = ('name', 'title')
```
In this example, the list view will display the ``name`` and ``title`` fields of each ``Author`` object.

You can also specify which fields are available for sorting by setting the ``sortable_by`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    sortable_by = ('name', 'title')  # List of fields available for sorting
```
In this example, users can sort the list view by the ``name`` or ``title`` fields.

### Customizing Search
You can enable search for the model by setting the ``search_fields`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    search_fields = ('name', 'title', 'birth_date')
```
In this example, users can search ``Author`` objects by their ``name``, ``title``, or ``birth_date`` fields.

### Customizing Inline Actions
You can add inline actions to the model by defining methods on your ``ModelFrontend`` subclass and including their names in the ``inline_button`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    inline_button = ('check', 'uncheck')

    def check(self, object):
        print(object.name)

    def uncheck(self, object):
        print(object.title)
```
In this example, each ``Author`` object in the list view will have a ``check`` and ``uncheck`` button. When clicked, these buttons will call the corresponding methods on the ``AuthorFrontend`` instance, passing the ``Author`` object as an argument.

### Customizing Toolbar Actions
Similarly, you can add toolbar actions by defining methods and including their names in the ``toolbar_button`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    toolbar_button = ('everything', 'everything_everything')

    def everything(self):
        print(self)

    def everything_everything(self):
        print(self)
```
In this example, the frontend will have a toolbar with an ``everything`` and ``everything_everything`` button. When clicked, these buttons will call the corresponding methods on the ``AuthorFrontend`` instance.

### Customizing Pagination
You can control how many objects are displayed per page in the list view by setting the ``list_per_page`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    list_per_page = 5
```
In this example, the list view will display 5 ``Author`` objects per page.

### Customizing Filters
You can add a sidebar for filtering the list view by setting the ``list_filter`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    list_filter = ('name', 'title')
```
In this example, the list view will include a sidebar that allows users to filter ``Author`` objects by their ``name`` or ``title`` fields.

### Customizing Read-Only Fields
You can specify which fields should be read-only by setting the ``readonly_fields`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    readonly_fields = ('name', 'title')
```
In this example, the ``name`` and ``title`` fields will be displayed as read-only.

### Customizing Cards
If you want to display your data in a card format, you can set the ``cards`` attribute to ``True``:

```python
class AuthorFrontend(frontend.ModelFrontend):
    cards = True
```
In this example, the ``Author`` objects will be displayed in a card format.

### Customizing Frontend Description
You can add a description to your frontend by setting the ``description`` attribute:

```python
class AuthorFrontend(frontend.ModelFrontend):
    description = f"everything_everything everything_everything everything_everything "
```
In this example, the description will be displayed on the frontend.

Remember to register your ``ModelFrontend`` subclass with ``frontend.site`` so that it is used:

```python
frontend.site.register(Author, AuthorFrontend)
```

This completes the overview of Django Fast Frontend customization. It offers a high level of customization to create a frontend that meets your application's specific needs. Keep in mind that not all features are covered here, so make sure to explore the Django Fast Frontend's documentation for more advanced features and options.


## The ModelFrontend Class
The ``ModelFrontend`` class is a major component of the Django frontend configuration. It inherits from the ``FrontendAbstract`` and ``NotImplementedMixin`` classes and provides a large number of methods and properties that you can use to customize the frontend view for a model.

Here are the primary components of the ``ModelFrontend`` class:

### Class Variables
The class variables in the ``ModelFrontend`` class are used to configure the frontend views. They include options for login requirements, toolbar buttons, list display fields, pagination, permissions, search, sorting, filtering, readonly fields, and more. Each of these class variables can be overridden in subclasses to provide custom configurations for different models.

### Initialization
The ``ModelFrontend`` class is initialized with a ``model`` keyword argument, which specifies the Django model to configure frontend settings for. This model is stored in the ``self.model`` instance variable.

```python
def __init__(self, *args, **kwargs):
    self.model = kwargs.get('model', None)
```

### Get Methods
The ``ModelFrontend`` class includes a number of get methods that return the values of the class variables. These methods can be overridden in subclasses to provide custom logic for determining the values of the class variables.

```python
def get_list_display(self):
    return self.list_display
```

### Queryset Method
The ``queryset`` method gets objects of the model with the specified fields. It uses the ``get_fields`` method to determine which fields to include in the queryset. If 'id' is included in the fields, then the queryset values are limited to those fields. If no fields are specified, then all fields except 'id' are included in the queryset values.

```python
def queryset(self, *args, **kwargs):
    ...
```

### Pagination Method
The ``get_pagination`` method gets a paginator for the objects and returns the paginated objects. It uses the ``get_list_per_page`` method to determine how many objects to include on each page.

```python
def get_pagination(self, request, objects):
    ...
```

### Model Actions Method
The ``get_model_actions`` method gets the actions to include in the table fields for the frontend view. If ``inline_button`` is defined, then these actions are added to the table fields.

```python
def get_model_actions(self, inline_button):
    ...
```

### Search, Filter, and Sort Methods
The ``get_search_results``, ``get_filter_results``, and ``get_sort_results`` methods are used to apply search, filter, and sort parameters to the objects queryset. They use the ``get_search_fields``, ``get_list_filter``, and ``get_sortable_by`` methods to determine which fields to use for searching, filtering, and sorting.

```python
def get_search_results(self, objects, search_fields, search_query):
    ...

def get_filter_results(self, objects, filter_fields, filter_args):
    ...

def get_sort_results(self, objects, sort_fields, sort_args):
    ...
```

### Filter Options and Args Methods
The ``get_filter_options`` and ``get_filter_args`` methods are used to get the filter options and arguments for the frontend view. They use the ``get_list_filter`` method to determine which fields to use for filtering.

```python
def get_filter_options(self):
    ...

def get_filter_args(self, request_get):
    ...
```

This class provides a comprehensive set of options and methods for customizing the frontend views for Django models


## Overriding ModelFrontend Methods
The ``ModelFrontend`` class methods provide a powerful way to control the behavior of the frontend configuration for a Django model. While the default methods provide a good starting point, you can override these methods in your own subclasses to provide custom functionality.

Here are some examples of how you can override these methods:

### Overriding the get_fields Method
You might want to display different fields in the frontend view depending on some condition. For example, you might want to display certain fields only to authenticated users. You can accomplish this by overriding the ``get_fields`` method and adding a check for the user's authentication status.

```python
def get_fields(self):
    if self.request.user.is_authenticated:
        return ('field1', 'field2', 'field3')
    else:
        return ('field1', 'field2')
```

### Overriding the get_search_results Method
You might want to customize the way search queries are handled. For example, you might want to perform case-insensitive searches or use a different search algorithm. You can accomplish this by overriding the ``get_search_results`` method.

```python
def get_search_results(self, objects, search_fields, search_query):
    # Perform a case-insensitive search
    query = Q()
    for field in search_fields:
        query |= Q(**{f"{field}__icontains": search_query})
    objects = objects.filter(query)
    return objects
```

### Overriding the get_pagination Method
You might want to customize the number of objects displayed per page or the way pagination is handled. You can do this by overriding the ``get_pagination`` method.

```python
def get_pagination(self, request, objects):
    # Display 50 items per page instead of the default 100
    paginator = Paginator(objects, 50)
    objects = paginator.get_page(request.GET.get("page"))
    return objects
```

By overriding these and other ``ModelFrontend`` methods, you can customize the frontend configuration for each Django model in your project.
