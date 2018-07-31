import random

from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import F
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, UpdateView
import itertools
from PokerApp.forms import CustomUserCreationForm, CustomUserChangeForm
from PokerApp.models import CustomUser, GameWithPlayers, CurrentGame, Bot, \
    CountSeat


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

    def get(self, request, username):

        user = CustomUser.objects.filter(username=username).all()
        bots = Bot.objects.filter().all()
        return render(request, 'lobby.html', locals())

    def post(self, request, username):

        suits = ["S", "D", "H", "C"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K",
                 "A"]
        cards_tuple = []

        for _ in itertools.product(suits, ranks):
            cards_tuple.append(_)

        community_cards = [cards[0] + cards[1] for cards in cards_tuple]
        random.shuffle(community_cards)

        current_user = CustomUser.objects.get(username=username)

        seat_1 = CountSeat.objects.get(id=1).seat_number
        if seat_1 != 6:
            seat_1 += 1
            CountSeat.objects.filter(id=1).update(seat_number=seat_1)
        elif seat_1 == 6:
            seat_1 = 1
            CountSeat.objects.filter(id=1).update(seat_number=seat_1)

        seat_2 = 0
        if seat_1 == 6:
            seat_2 = 1
        else:
            seat_2 = seat_1 + 1

        game_1_start = CurrentGame.objects.create(
            small_blind=1,
            big_blind=2,
            small_blind_seat=seat_1,
            big_blind_seat=seat_2,
            bank=3,
            flop_1_card=community_cards.pop(),
            flop_2_card=community_cards.pop(),
            flop_3_card=community_cards.pop(),
            turn=community_cards.pop(),
            river=community_cards.pop()
        )

        GameWithPlayers.objects.create(
            player_user=current_user,
            position=1,
            handled_card_1=community_cards.pop(),
            handled_card_2=community_cards.pop(),
            current_stack=50,
            game=game_1_start
        )

        for i in range(1, 6):
            GameWithPlayers.objects.create(
                player_bot_id=i,
                handled_card_1=community_cards.pop(),
                handled_card_2=community_cards.pop(),
                position=i+1,
                current_stack=50,
                game=game_1_start
            )

        game_data = CurrentGame.objects.last()
        data = GameWithPlayers.objects.filter(game=game_1_start).all()

        for player in data:
            if game_data.small_blind_seat == player.position:
                player.current_stack = \
                    player.current_stack - game_data.small_blind
            elif game_data.big_blind_seat == player.position:
                player.current_stack = \
                    player.current_stack - game_data.big_blind

        return render(request, 'game.html', locals())
