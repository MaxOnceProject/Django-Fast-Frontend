from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from app.models import Author


class Command(BaseCommand):
    help = "Create deterministic demo data for Docker end-to-end tests."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="ui-user")
        parser.add_argument("--password", default="top_secret")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        Author.objects.all().delete()
        User.objects.filter(username=username).delete()

        User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password,
        )

        Author.objects.bulk_create([
            Author(name="Ada", title="Dr"),
            Author(name="Grace", title="Ms"),
            Author(name="Marie", title="Prf"),
        ])

        self.stdout.write(self.style.SUCCESS("Created demo UI test data."))