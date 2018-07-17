from ...models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        Bot.objects.create(
            bot_name='Petr',

        )
