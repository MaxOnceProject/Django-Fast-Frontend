import frontend
from app2.models import People


# Register your models here.
class PeopleFrontend(frontend.ModelFrontend):
    fields = ('id', 'birth_date')

frontend.site.register(People, PeopleFrontend)
