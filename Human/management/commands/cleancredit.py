import getpass

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from Human.models import Link, Credit
from LineMe.constants import PROJECT_NAME, LINK_BONUS


class Command(BaseCommand):
    help = 'Clean Links Credits'

    def handle(self, *args, **options):
        for link in Link.objects.all():
            if link.status == 3:
                if not Credit.objects.filter(link=link).exists():
                    print 'Link: ', link.id
                    now = timezone.now()
                    link.creator.extra.credits += LINK_BONUS
                    link.creator.extra.save()

                    c = Credit(user=link.creator,
                               link=link,
                               action=LINK_BONUS,
                               timestamp=now)
                    c.save()





