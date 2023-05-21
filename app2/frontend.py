import frontend
from app2.models import People


# Register your models here.
@frontend.register(People)
class PeopleFrontend(frontend.ModelFrontend):
    # list_display = ('name', 'title', 'birth_date')
    # login_required = False
    pass

# frontend.site.register(People, PeopleFrontend)
