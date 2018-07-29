import random

from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, UpdateView, RedirectView
import itertools
from PokerApp.forms import CustomUserCreationForm, CustomUserChangeForm
from PokerApp.models import CustomUser, GameWithPlayers, CurrentGame


def main(request):
    data = CurrentGame.objects.last()
    return render(request, 'base.html', {'game_data': data})


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


class StartGame(View):

    def get(self, request):
        suits = ["S", "D", "H", "C"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K",
                 "A"]
        cards_tuple = []

        for _ in itertools.product(suits, ranks):
            cards_tuple.append(_)

        community_cards = [cards[0] + cards[1] for cards in cards_tuple]
        random.shuffle(community_cards)

        game_1_start = CurrentGame.objects.create(
            small_blind=1,
            big_blind=2,
            bank=3,
            flop_1_card=community_cards.pop(),
            flop_2_card=community_cards.pop(),
            flop_3_card=community_cards.pop()
        )

        GameWithPlayers.objects.create(
            player_user_id=1,
            seat=1,
            handled_card_1=community_cards.pop(),
            handled_card_2=community_cards.pop(),
            current_stack=50,
            game=game_1_start
        )

        for i in range(2, 7):
            GameWithPlayers.objects.create(
                player_bot_id=i-1,
                seat=i,
                handled_card_1=community_cards.pop(),
                handled_card_2=community_cards.pop(),
                current_stack=50,
                game=game_1_start

            )

        game_data = CurrentGame.objects.last()
        data = GameWithPlayers.objects.filter(game=game_1_start).all()
        return render(request, 'game.html', locals())
