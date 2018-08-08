import random
from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import F, Q
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, UpdateView, TemplateView
import itertools
from PokerApp.forms import CustomUserCreationForm, CustomUserChangeForm
from PokerApp.handler_function_for_seat import current_player_position
from PokerApp.handlers import hand_power, change_position, combination
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

        PositionOfCurrentPlayer.objects.filter(id=1).update(status='EP')

        seat_1 = CountSeat.objects.get(id=1).seat_number
        if seat_1 != 6:
            seat_1 += 1
            CountSeat.objects.filter(id=1).update(seat_number=seat_1)
        elif seat_1 == 6:
            seat_1 = 1
            CountSeat.objects.filter(id=1).update(seat_number=seat_1)

        seat_2 = 1 if seat_1 == 6 else seat_1 + 1

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
            current_stack=200,
            game=game_1_start
        )

        for i in range(1, 6):
            GameWithPlayers.objects.create(
                player_bot_id=i,
                handled_card_1=community_cards.pop(),
                handled_card_2=community_cards.pop(),
                position=i + 1,
                current_stack=200,
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


class StartGame(TemplateView):
    template_name = 'game.html'

    def get_context_data(self, **kwargs):
        context = super(StartGame, self).get_context_data(**kwargs)
        game_data = CurrentGame.objects.last()
        data = GameWithPlayers.objects.filter(game=game_data).all()
        status = PositionOfCurrentPlayer.objects.get().status
        action_data = GameWithPlayers.objects.filter(game=game_data).all()
        actions = [action.action_preflop for action in action_data]

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in data
        }

        seat_of_curr_pos = players_positions.get(status)

        context['data'] = data
        context['game_data'] = game_data
        context['seat'] = seat_of_curr_pos
        context['actions'] = actions
        return context

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
                        action_preflop='Raise',
                        current_stack=F('current_stack') - wage,
                        wage=wage
                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + wage
                    )

                elif hand_value is True and status == 'MP':
                    if GameWithPlayers.objects.get(
                            player_bot__bot_name=players_positions.get(
                                'EP'),
                            game=game_object).action_preflop == 'Raise':
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Call',
                            current_stack=F('current_stack') - wage,
                            wage=wage
                        )
                        CurrentGame.objects.filter(id=game_object.id).update(
                            bank=F('bank') + wage
                        )

                    else:
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Raise',
                            current_stack=F('current_stack') - wage,
                            wage=wage
                        )
                        CurrentGame.objects.filter(id=game_object.id).update(
                            bank=F('bank') + wage
                        )

                elif hand_value is True and status == 'CO':
                    if GameWithPlayers.objects.get(
                            player_bot__bot_name=players_positions.get(
                                'EP'),
                            game=game_object).action_preflop == 'Fold' and \
                            GameWithPlayers.objects.get(
                                player_bot__bot_name=players_positions.get(
                                    'MP'),
                                game=game_object).action_preflop == 'Fold':
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Raise',
                            current_stack=F('current_stack') - wage,
                            wage=wage
                        )
                        CurrentGame.objects.filter(id=game_object.id).update(
                            bank=F('bank') + wage
                        )

                    else:
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Call',
                            current_stack=F('current_stack') - wage,
                            wage=wage
                        )
                        CurrentGame.objects.filter(id=game_object.id).update(
                            bank=F('bank') + wage
                        )

                elif hand_value is True and status == 'BU':
                    if GameWithPlayers.objects.get(
                            player_bot__bot_name=players_positions.get(
                                'EP'),
                            game=game_object).action_preflop == 'Fold' and \
                            GameWithPlayers.objects.get(
                                player_bot__bot_name=players_positions.get(
                                    'MP'),
                                game=game_object).action_preflop == 'Fold' and \
                            GameWithPlayers.objects.get(
                                player_bot__bot_name=players_positions.get(
                                    'CO'),
                                game=game_object).action_preflop == 'Fold':
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Raise',
                            current_stack=F('current_stack') - wage,
                            wage=wage,
                        )
                        CurrentGame.objects.filter(id=game_object.id).update(
                            bank=F('bank') + wage
                        )

                    else:
                        wage = 3 * game_object.big_blind
                        player_from_base.update(
                            action_preflop='Call',
                            current_stack=F('current_stack') - wage,
                            wage=wage
                        )
                        CurrentGame.objects.filter(id=game_object.id).update(
                            bank=F('bank') + wage
                        )

                elif hand_value is True and status == 'SB':
                    wage = 2 * game_object.big_blind + game_object.small_blind
                    player_from_base.update(
                        action_preflop='Call',
                        current_stack=F('current_stack') - wage,
                        wage=wage + game_object.small_blind
                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + wage
                    )

                elif hand_value is True and status == 'BB':
                    wage = 2 * game_object.big_blind
                    player_from_base.update(
                        action_preflop='Call',
                        current_stack=F('current_stack') - wage,
                        wage=wage + game_object.big_blind
                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + wage
                    )

                elif hand_value is False:

                    player_from_base.update(action_preflop='Fold')

                PositionOfCurrentPlayer.objects.filter(status=status).update(
                    status=change_position(status))
            elif current_player == username:
                wage = request.POST.get('raise_number')
                GameWithPlayers.objects.filter(
                    game=game_object, player_user__username=username, ).update(
                    action_preflop='Raise',
                    current_stack=F('current_stack') - wage,
                    wage=wage
                )
                CurrentGame.objects.filter(id=game_object.id).update(
                    bank=F('bank') + wage
                )

                PositionOfCurrentPlayer.objects.filter(status=status).update(
                    status=change_position(status))

        return redirect('game', username)


def fold(request, username):
    game_obj = CurrentGame.objects.last()
    GameWithPlayers.objects.filter(player_user__username=username,
                                   game=game_obj).update(
        action_preflop='Fold')
    seat = PositionOfCurrentPlayer.objects.get().status
    PositionOfCurrentPlayer.objects.filter(status=seat).update(
        status=change_position(seat))
    return redirect('game', username)


def call(request, username):
    game_data = CurrentGame.objects.last()
    position = current_player_position(
        GameWithPlayers.objects.get(
            game=game_data, player_user__username=username).position,
        game_data.big_blind_seat,
        game_data.small_blind_seat)
    if position != 'SB' and position != 'BB':
        wage = 3 * game_data.big_blind
        GameWithPlayers.objects.filter(player_user__username=username,
                                       game=game_data).update(
            action_preflop='Call',
            current_stack=F('current_stack') - wage,
            wage=wage
        )
        CurrentGame.objects.filter(id=game_data.id).update(
            bank=F('bank') + wage
        )
    elif position == 'SB':
        wage = 2 * game_data.big_blind + game_data.small_blind
        GameWithPlayers.objects.filter(player_user__username=username,
                                       game=game_data).update(
            action_preflop='Call',
            current_stack=F('current_stack') - wage,
            wage=wage + game_data.small_blind
        )
        CurrentGame.objects.filter(id=game_data.id).update(
            bank=F('bank') + wage
        )
    seat = PositionOfCurrentPlayer.objects.get().status
    PositionOfCurrentPlayer.objects.filter(status=seat).update(
        status=change_position(seat))
    return redirect('game', username)


def check(request, username):
    game_obj = CurrentGame.objects.last()
    GameWithPlayers.objects.filter(player_user__username=username,
                                   game=game_obj).update(
        action_preflop='Check')
    seat = PositionOfCurrentPlayer.objects.get().status
    PositionOfCurrentPlayer.objects.filter(status=seat).update(
        status=change_position(seat))
    return redirect('game', username)


class FlopRound(TemplateView):
    template_name = 'game_flop.html'

    def get_context_data(self, **kwargs):
        context = super(FlopRound, self).get_context_data(**kwargs)
        status = 'SB'
        PositionOfCurrentPlayer.objects.filter(id=1).update(status=status)
        game_data = CurrentGame.objects.last()
        data = GameWithPlayers.objects.filter(Q(
            game=game_data,
            action_preflop__startswith='R') | Q(
            game=game_data,
            action_preflop__startswith='C') | Q(
            game=game_data,
            action_preflop__startswith='B')).all()

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in data
        }

        seat_of_curr_pos = players_positions.get(status)

        context['data'] = data
        context['game_data'] = game_data
        context['seat'] = seat_of_curr_pos
        return context

    def post(self, request, username):
        game_data = CurrentGame.objects.last()
        players = GameWithPlayers.objects.filter(Q(
            game=game_data,
            action_preflop__startswith='R') | Q(
            game=game_data,
            action_preflop__startswith='C') | Q(
            game=game_data,
            action_preflop__startswith='B')).all()

        bluff_index = random.randint(1, 7)

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in players
        }

        status = PositionOfCurrentPlayer.objects.get().status

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=players_positions.get(status)
        )
        if current_player.player_bot:
            current_combo = combination(
                current_player.handled_card_1 + current_player.handled_card_2,
                game_data.flop_1_card + game_data.flop_2_card +
                game_data.flop_3_card
            )
            if current_player.action_preflop.startswith('R') or \
                    current_player.action_preflop.startswith('B'):
                if current_combo:
                    bet = game_data.bank * 0.6
                    GameWithPlayers.objects.filter(
                        game=game_data, position=current_player.position
                    ).update(
                        action_preflop='Bet',
                        wage=bet,
                        current_stack=F('current_stack') - F('wage')
                    )
                    CurrentGame.objects.filter(id=game_data.id).update(
                        bank=F('bank') + bet
                    )
                else:
                    if bluff_index == 2 or bluff_index == 3 or bluff_index == 5:
                        GameWithPlayers.objects.filter(
                            game=game_data, position=current_player.position
                        ).update(action_preflop='Check')
                    else:
                        bet = game_data.bank * 0.6
                        GameWithPlayers.objects.filter(
                            game=game_data, position=current_player.position
                        ).update(
                            action_preflop='Bet',
                            wage=bet,
                            current_stack=F('current_stack') - F('wage')
                        )
                        CurrentGame.objects.filter(id=game_data.id).update(
                            bank=F('bank') + bet
                        )
            elif current_player.action_preflop.startswith('C'):
                if status == 'SB':
                    GameWithPlayers.objects.filter(
                        game=game_data, position=players_positions.get(status)
                    ).update(
                        action_preflop='Check'
                    )
                elif status == 'BB':
                    if GameWithPlayers.objects.get(
                            game=game_data, position=players_positions.get('SB')
                    ).action_preflop == 'Bet':
                        if current_combo:
                            GameWithPlayers.objects.filter(
                                game=game_data, position=current_player.position
                            ).update(
                                action_preflop='Call',
                                wage=GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('SB')).wage,
                                current_stack=F('current_stack') - F('wage')
                            )
                        else:
                            GameWithPlayers.objects.filter(
                                game=game_data, position=current_player.position
                            ).update(action_preflop='Fold')
                    elif not players_positions.get(
                            'EP') and not players_positions.get(
                        'MP') and not players_positions.get(
                        'CO') and not players_positions.get(
                        'BU') and GameWithPlayers.objects.get(
                        game=game_data, position=players_positions.get('SB')
                    ).action_preflop.startswith('C'):
                        if current_combo:
                            bet = game_data.bank * 0.6
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=current_player.position
                            ).update(
                                action_preflop='Bet',
                                wage=bet,
                                current_stack=F('current_stack') - F('wage')
                            )
                            CurrentGame.objects.filter(
                                id=game_data.id).update(
                                bank=F('bank') + bet
                            )
                        else:
                            if bluff_index in range(1, 5):
                                bet = game_data.bank * 0.6
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Bet',
                                    wage=bet,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + bet
                                )
                    else:
                        GameWithPlayers.objects.filter(
                            game=game_data, position=current_player.position
                        ).update(action_preflop='Check')
                elif status == 'EP':
                    if players_positions.get(status):
                        if GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('SB')
                        ).action_preflop == 'Bet':
                            if current_combo:
                                bet = GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('SB')
                                ).wage
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=bet,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + bet
                                )
                        elif GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('BB')
                        ).action_preflop == 'Bet':
                            if current_combo:
                                bet = GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get(
                                        'BB')).wage
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=bet,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + bet
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Fold')
                        else:
                            GameWithPlayers.objects.filter(
                                game=game_data, position=current_player.position
                            ).update(action_preflop='Check')
                    else:
                        PositionOfCurrentPlayer.objects.filter(id=1).update(
                            status=change_position(status))
