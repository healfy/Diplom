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
from PokerApp.handler_function_for_seat import current_player_position
from PokerApp.handlers import hand_power, change_position
from PokerApp.models import *


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


class LobbyView(View):

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
                position=i + 1,
                current_stack=50,
                game=game_1_start
            )
        data = GameWithPlayers.objects.filter(game=game_1_start).all()

        for player in data:
            if game_1_start.small_blind_seat == player.position:
                player.current_stack = \
                    player.current_stack - game_1_start.small_blind
                GameWithPlayers.objects.filter(
                    position=game_1_start.small_blind_seat,
                    game=game_1_start).update(
                    current_stack=player.current_stack
                )
            elif game_1_start.big_blind_seat == player.position:
                player.current_stack = \
                    player.current_stack - game_1_start.big_blind
                GameWithPlayers.objects.filter(
                    position=game_1_start.big_blind_seat,
                    game=game_1_start).update(
                    current_stack=player.current_stack
                )

        return redirect('game', current_user.username)


class StartGame(View):

    def get(self, request, username):

        game_data = CurrentGame.objects.last()
        data = GameWithPlayers.objects.filter(game=game_data).all()

        return render(request, 'game.html', {'data': data})

    def post(self, request, username):
        game_object = CurrentGame.objects.last()
        status = PositionOfCurrentPlayer.objects.get().status
        action_data = GameWithPlayers.objects.filter(game=game_object).all()
        actions = [action.action_preflop for action in action_data]

        players_bot = [
            GameWithPlayers.objects.get(
                game=game_object, player_bot_id=i) for i in range(1, 6)
        ]

        players_positions = {
            current_player_position(
                player.position, game_object.big_blind_seat,
                game_object.small_blind_seat): player.current_player.bot_name
            for player in players_bot
        }

        players_positions[current_player_position(
            GameWithPlayers.objects.get(
                game=game_object, player_user__username=username).position,
            game_object.big_blind_seat,
            game_object.small_blind_seat)] = GameWithPlayers.objects.get(
            game=game_object, player_user__username=username
        ).current_player.username

        if None in actions:

            current_player = players_positions.get(status)

            player_from_base = GameWithPlayers.objects.filter(
                game=game_object,
                player_bot__bot_name=current_player)

            if current_player != username:

                hand_value = hand_power(
                    GameWithPlayers.objects.get(
                        game=game_object,
                        player_bot__bot_name=current_player).handled_card_1,
                    GameWithPlayers.objects.get(
                        game=game_object,
                        player_bot__bot_name=current_player).handled_card_2,
                    status
                )

                if hand_value is True and status == 'EP':
                    wage = 3 * game_object.big_blind
                    player_from_base.update(
                        action_preflop='Raise'
                    )
                    player_from_base.update(
                        current_stack=F('current_stack') - wage
                    )
                elif hand_value is True and status == 'MP':
                    if GameWithPlayers.objects.get(
                            player_bot__bot_name=players_positions.get(
                                'EP')).action_preflop == 'Raise':
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Call'
                        )
                        player_from_base.update(
                            current_stack=F('current_stack') - wage
                        )
                    else:
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Raise'
                        )
                        player_from_base.update(
                            current_stack=F('current_stack') - wage
                        )
                elif hand_value is True and status == 'CO':
                    if GameWithPlayers.objects.get(
                            player_bot__bot_name=players_positions.get(
                                'EP')).action_preflop == 'Fold' and \
                            GameWithPlayers.objects.get(
                                player_bot__bot_name=players_positions.get(
                                    'MP')).action_preflop == 'Fold':
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Raise'
                        )
                        player_from_base.update(
                            current_stack=F('current_stack') - wage
                        )
                    else:
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Call'
                        )
                        player_from_base.update(
                            current_stack=F('current_stack') - wage
                        )
                elif hand_value is True and status == 'BU':
                    if GameWithPlayers.objects.get(
                            player_bot__bot_name=players_positions.get(
                                'EP')).action_preflop == 'Fold' and \
                            GameWithPlayers.objects.get(
                        player_bot__bot_name=players_positions.get(
                            'MP')).action_preflop == 'Fold' and \
                            GameWithPlayers.objects.get(
                        player_bot__bot_name=players_positions.get(
                            'CO')).action_preflop == 'Fold':
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Raise'
                        )
                        player_from_base.update(
                            current_stack=F('current_stack') - wage
                        )
                    else:
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Call'
                        )
                        player_from_base.update(
                            current_stack=F('current_stack') - wage
                        )
                elif hand_value is True and status == 'SB':
                    wage = 2 * game_object.big_blind + game_object.small_blind
                    player_from_base.update(
                        action_preflop='Call'
                    )
                    player_from_base.update(
                        current_stack=F('current_stack') - wage
                    )
                elif hand_value is True and status == 'BB':
                    wage = 2 * game_object.big_blind
                    player_from_base.update(
                        action_preflop='Call'
                    )
                    player_from_base.update(
                        current_stack=F('current_stack') - wage
                    )
                elif hand_value is False:

                    player_from_base.update(action_preflop='Fold')
            # elif current_player == username:

        PositionOfCurrentPlayer.objects.filter(status=status).update(
            status=change_position(status))

        return redirect('game', username)
