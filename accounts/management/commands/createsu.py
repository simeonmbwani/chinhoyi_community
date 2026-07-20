from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a default superuser if none exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = "simeonmbwani"
        email = "simeonmbwani@gmail.com"
        password = "@A1n2d3y4" 

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists."))
