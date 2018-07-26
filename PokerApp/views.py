import random

from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, UpdateView
import itertools
import os
from PokerApp.forms import CustomUserCreationForm, CustomUserChangeForm
from PokerApp.models import CustomUser, Bot, GameWithPlayers, CurrentGame


def main(request):
    return render(request, 'index.html')


class RegisterFormView(FormView):
    form_class = CustomUserCreationForm
    success_url = "/login/"
    template_name = "registration.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = "/"

    def form_valid(self, form):
        self.user = form.get_user()

        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")


def profile(request, username):
    user = CustomUser.objects.filter(username=username).all()
    return render(request, 'profile.html', {'user_object': user})


class UpdateProfile(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile_editing.html'
    success_url = '/'


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def game(request):
    user_active = CustomUser.objects.filter().all()
    for field in user_active:
        print(field.username, field.last_name, field.first_name)
    return render(request, 'game.html', locals())


class StartGame(View):
    suits = ["S", "D", "H", "C"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    cards_tuple = []

    for i in itertools.product(suits, ranks):
        cards_tuple.append(i)

    community_cards = [cards[0] + cards[1] for cards in cards_tuple]

    def get(self, request):

        # game_1_start = CurrentGame.objects.create(
        #     small_blind=10,
        #     big_blind=20,
        #     bank=30
        #
        # )
        # GameWithPlayers.objects.create(
        #     player_user_id=1,
        #     seat=1,
        #     handled_card_1='SA',
        #     handled_card_2='HA',
        #     current_stack=50,
        #     game=game_1_start
        # )
        # GameWithPlayers.objects.create(
        #     player_bot_id=1,
        #     seat=2,
        #     handled_card_1='S6',
        #     handled_card_2='D6',
        #     current_stack=50,
        #     game=game_1_start
        #
        # )
        # GameWithPlayers.objects.create(
        #     player_bot_id=2,
        #     seat=3,
        #     handled_card_1='H6',
        #     handled_card_2='D7',
        #     current_stack=50,
        #     game=game_1_start
        # )
        # GameWithPlayers.objects.create(
        #     player_bot_id=3,
        #     seat=4,
        #     handled_card_1='S9',
        #     handled_card_2='D8',
        #     current_stack=50,
        #     game=game_1_start
        # )
        # GameWithPlayers.objects.create(
        #     player_bot_id=4,
        #     seat=5,
        #     handled_card_1='D2',
        #     handled_card_2='D3',
        #     current_stack=50,
        #     game=game_1_start
        # )
        # GameWithPlayers.objects.create(
        #     player_bot_id=5,
        #     seat=6,
        #     handled_card_1='CA',
        #     handled_card_2='DK',
        #     current_stack=50,
        #     game=game_1_start
        # )
        card1 = random.choice(self.community_cards)
        self.community_cards.remove(card1)
        card2 = random.choice(self.community_cards)
        self.community_cards.remove(card2)
        card3 = random.choice(self.community_cards)
        self.community_cards.remove(card3)
        data = GameWithPlayers.objects.filter().all()
        return render(request, 'game.html', locals())

