import frontend
from app2.models import People


# Register your models here.
class PeopleFrontend(frontend.ModelFrontend):
    list_display = ('name', 'title', 'birth_date')
    login_required = False

frontend.site.register(People, PeopleFrontend)
