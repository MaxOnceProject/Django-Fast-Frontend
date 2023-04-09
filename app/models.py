from django.db import models

# Create your models here.
class Author(models.Model):
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        db_table_comment = "A List of Authors"

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=3)
    birth_date = models.DateField(blank=True, null=True)
