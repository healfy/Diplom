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


class CurrentGame(models.Model):
    bank = models.IntegerField(verbose_name='bank')
    big_blind = models.IntegerField(verbose_name='big_blind')
    small_blind = models.IntegerField(verbose_name='small_blind')
    small_blind_seat = models.IntegerField(default=0)
    big_blind_seat = models.IntegerField(default=0)
    flop_1_card = models.CharField(blank=True, null=True, max_length=20)
    flop_2_card = models.CharField(blank=True, null=True, max_length=20)
    flop_3_card = models.CharField(blank=True, null=True, max_length=20)
    turn = models.CharField(blank=True, null=True, max_length=20)
    river = models.CharField(blank=True, null=True, max_length=20)
    winner = models.CharField(verbose_name='winner', max_length=20)


class GameWithPlayers(models.Model):
    player_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_player',
        blank=True,
        null=True
        )
    player_bot = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
        related_name='bot_player',
        blank=True,
        null=True
    )

    @property
    def current_player(self):
        return self.player_bot or self.player_user

    game = models.ForeignKey(
        CurrentGame,
        on_delete=models.CASCADE,
        related_name='game_property'
    )
    handled_card_1 = models.CharField(
        max_length=20,
        unique=False,
        verbose_name='first_card')
    handled_card_2 = models.CharField(
        max_length=20,
        unique=False,
        verbose_name='second_card')
    position = models.IntegerField(default=0)
    current_stack = models.IntegerField(default=0)
    action_preflop = models.CharField(max_length=20, null=True, blank=True)
    wage = models.PositiveIntegerField(default=0)


class CountSeat(models.Model):
    seat_number = models.PositiveIntegerField(default=0)


class PositionOfCurrentPlayer(models.Model):
    status = models.CharField(max_length=10)
