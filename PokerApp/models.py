from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(verbose_name='username',
                                max_length=130,
                                unique=True)
    email = models.EmailField(verbose_name='email address')
    date_joined = models.DateTimeField(verbose_name='date joined',
                                       default=timezone.now)
    balance = models.IntegerField(verbose_name='Stack', default=100,
                                  auto_created=True)

    def __str__(self):
        return self.username


class Bot(models.Model):
    bot_name = models.CharField(verbose_name='Bot_name', max_length=20,
                                unique=True)
    bot_balance = models.IntegerField(verbose_name='Bot_stack', default=1000,
                                      auto_created=True)
    bot_image = models.ImageField(upload_to='static/images', blank=True,
                                  null=True,
                                  verbose_name='Bot_image')
