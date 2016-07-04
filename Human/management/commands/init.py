import getpass

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from Human.constants import PROJECT_NAME


class Command(BaseCommand):
    help = 'Create dummy data - id from 10000'

    def handle(self, *args, **options):
        return





