from django.contrib import admin

from app.models import Author


# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fields = ('name', 'title')
    list_filter = ('name', 'title', 'birth_date')  # List of fields available for filtering

