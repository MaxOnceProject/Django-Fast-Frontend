from django.contrib import admin

from app2.models import People


# Register your models here.
@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    fields = ('name', 'title')
