from django.db import models

# Create your models here.
class People(models.Model):
    class Meta:
        verbose_name = "People"
        verbose_name_plural = "People"

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=3)
    birth_date = models.DateField(blank=True, null=True)
