import frontend
from app.models import Author

@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title', 'created_at')
    login_required = False
    list_display = ('name', 'title')
    inline_button = ('check', 'uncheck')
    readonly_fields = ('created_at',)
    # view_permission = False
    cards = True
    list_filter = ('name', 'title')
    search_fields = ('name', 'title', 'birth_date')
    change_permission = True
    add_permission = True
    # delete_permission = True
    # list_per_page = 5
    toolbar_button = ('everything', 'everything_everything')
    # description = f"everything_everything everything_everything everything_everything "
    sortable_by = ('name', 'title')  # List of fields available for sorting

    @frontend.action(description='Do Everything')
    def everything(self):
        print(self)

    @frontend.action(description='Do Everything Twice')
    def everything_everything(self):
        print(self)

    @frontend.action(description='Mark As Checked')
    def check(self, object):
        print(object.name)

    @frontend.action(description='Mark As Unchecked')
    def uncheck(self, object):
        print(object.title)
