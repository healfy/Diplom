from ...models import *
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        Bot.objects.create(
            bot_name='Petr',
            bot_image=os.path.join('static', 'images', 'android-pegatina.png')
        )
        Bot.objects.create(
            bot_name='Dima',
            bot_image=os.path.join('static', 'images', 'android-pegatina.png')
        )
        Bot.objects.create(
            bot_name='Ivan',
            bot_image=os.path.join('static', 'images', 'android-pegatina.png')
        )
        Bot.objects.create(
            bot_name='Nikola',
            bot_image=os.path.join('static', 'images', 'android-pegatina.png')
        )
        Bot.objects.create(
            bot_name='Viktor',
            bot_image=os.path.join('static', 'images', 'android-pegatina.png')
        )
