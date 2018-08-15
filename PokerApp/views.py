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
    return render(request, 'index.html', {'game_data': data})


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
        PositionOfCurrentPlayer.objects.filter(id=2).update(status='SB')

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
            river=community_cards.pop(),
            user=current_user
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
        print()
        context = super(StartGame, self).get_context_data(**kwargs)
        game_data = CurrentGame.objects.filter(
            user__username=self.args[0]).last()
        data = GameWithPlayers.objects.filter(game=game_data).all()
        status = PositionOfCurrentPlayer.objects.get(id=1).status
        action_data = GameWithPlayers.objects.filter(game=game_data).all()
        actions = [action.action_preflop for action in action_data]

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in data
        }

        seat_of_curr_pos = players_positions.get(status)

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=seat_of_curr_pos
        )

        context['data'] = data
        context['game_data'] = game_data
        context['seat'] = seat_of_curr_pos
        context['actions'] = actions
        context['current_player'] = current_player
        return context

    def post(self, request, username):
        game_object = CurrentGame.objects.filter(user__username=username).last()
        status = PositionOfCurrentPlayer.objects.get(id=1).status
        action_data = GameWithPlayers.objects.filter(game=game_object).all()

        players_positions = {
            current_player_position(
                player.position, game_object.big_blind_seat,
                game_object.small_blind_seat): player.position
            for player in action_data
        }

        current_player = GameWithPlayers.objects.get(
            game=game_object, position=players_positions.get(status)
        )

        if current_player.player_bot:
            player_from_base = GameWithPlayers.objects.filter(
                game=game_object,
                position=players_positions.get(status)).all()

            hand_value = hand_power(
                GameWithPlayers.objects.get(
                    game=game_object,
                    position=players_positions.get(status)).handled_card_1,
                GameWithPlayers.objects.get(
                    game=game_object,
                    position=players_positions.get(status)).handled_card_2,
                status
            )

            if hand_value is True and status == 'EP':
                player_from_base.update(
                    action_preflop='Raise',
                    wage=3 * game_object.big_blind,
                    current_stack=F('current_stack') - F('wage')

                )
                CurrentGame.objects.filter(id=game_object.id).update(
                    bank=F('bank') + 3 * game_object.big_blind
                )

            elif hand_value is True and status == 'MP':
                if GameWithPlayers.objects.get(
                        position=players_positions.get('EP'),
                        game=game_object).action_preflop == 'Raise':
                    player_from_base.update(
                        action_preflop='Call',
                        wage=3 * game_object.big_blind,
                        current_stack=F('current_stack') - F('wage')

                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + 3 * game_object.big_blind
                    )

                else:
                    player_from_base.update(
                        action_preflop='Raise',
                        wage=3 * game_object.big_blind,
                        current_stack=F('current_stack') - F('wage')

                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + 3 * game_object.big_blind
                    )

            elif hand_value is True and status == 'CO':
                if GameWithPlayers.objects.get(
                        position=players_positions.get('EP'),
                        game=game_object).action_preflop == 'Fold' and \
                        GameWithPlayers.objects.get(
                            position=players_positions.get('MP'),
                            game=game_object).action_preflop == 'Fold':
                    player_from_base.update(
                        action_preflop='Raise',
                        wage=3 * game_object.big_blind,
                        current_stack=F('current_stack') - F('wage')

                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + 3 * game_object.big_blind
                    )

                else:
                    player_from_base.update(
                        action_preflop='Call',
                        wage=3 * game_object.big_blind,
                        current_stack=F('current_stack') - F('wage')

                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + 3 * game_object.big_blind
                    )

            elif hand_value is True and status == 'BU':
                if GameWithPlayers.objects.get(
                        position=players_positions.get('EP'),
                        game=game_object).action_preflop == 'Fold' and \
                        GameWithPlayers.objects.get(
                            position=players_positions.get('MP'),
                            game=game_object).action_preflop == 'Fold' and \
                        GameWithPlayers.objects.get(
                            position=players_positions.get('CO'),
                            game=game_object).action_preflop == 'Fold':
                    player_from_base.update(
                        action_preflop='Raise',
                        wage=3 * game_object.big_blind,
                        current_stack=F('current_stack') - F('wage')

                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + 3 * game_object.big_blind
                    )

                else:
                    player_from_base.update(
                        action_preflop='Call',
                        wage=3 * game_object.big_blind,
                        current_stack=F('current_stack') - F('wage')

                    )
                    CurrentGame.objects.filter(id=game_object.id).update(
                        bank=F('bank') + 3 * game_object.big_blind
                    )

            elif hand_value is True and status == 'SB':
                wage = 2 * game_object.big_blind + game_object.small_blind
                player_from_base.update(
                    action_preflop='Call',
                    current_stack=F('current_stack') - wage,
                    wage=3 * game_object.big_blind
                )
                CurrentGame.objects.filter(id=game_object.id).update(
                    bank=F('bank') + wage
                )

            elif hand_value is True and status == 'BB':
                player_from_base.update(
                    action_preflop='Call',
                    wage=2 * game_object.big_blind,
                    current_stack=F('current_stack') - F('wage')

                )
                CurrentGame.objects.filter(id=game_object.id).update(
                    bank=F('bank') + 2 * game_object.big_blind
                )

            elif hand_value is False:

                player_from_base.update(action_preflop='Fold')

            PositionOfCurrentPlayer.objects.filter(id=1).update(
                status=change_position(status))
        else:
            GameWithPlayers.objects.filter(
                game=game_object, player_user__username=username, ).update(
                action_preflop='Raise',
                current_stack=F(
                    'current_stack') - request.POST.get('raise_number'),
                wage=request.POST.get('raise_number')
            )
            CurrentGame.objects.filter(id=game_object.id).update(
                bank=F('bank') + request.POST.get('raise_number')
            )

            PositionOfCurrentPlayer.objects.filter(id=1).update(
                status=change_position(status))
        return redirect('game', username)


def fold(request, username):
    game_obj = CurrentGame.objects.last()
    GameWithPlayers.objects.filter(player_user__username=username,
                                   game=game_obj).update(
        action_preflop='Fold')
    if 'flop' in request.path:
        PositionOfCurrentPlayer.objects.filter(id=2).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=2).status))
        return redirect('flop', username)
    elif 'turn' in request.path:
        PositionOfCurrentPlayer.objects.filter(id=2).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=2).status))
        return redirect('turn', username)
    else:
        PositionOfCurrentPlayer.objects.filter(id=1).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=1).status))
        return redirect('game', username)


def call(request, username):
    game_data = CurrentGame.objects.last()
    position = current_player_position(
        GameWithPlayers.objects.get(
            game=game_data,
            player_user__username=username
        ).position,
        game_data.big_blind_seat,
        game_data.small_blind_seat)
    if 'flop' in request.path:
        bet = GameWithPlayers.objects.get(
            game=game_data, action_preflop='Bet'
        ).wage
        GameWithPlayers.objects.filter(
            player_user__username=username,
            game=game_data).update(
            action_preflop='Call',
            current_stack=F('current_stack') - bet,
            wage=bet
        )
        CurrentGame.objects.filter(id=game_data.id).update(
            bank=F('bank') + bet
        )

        PositionOfCurrentPlayer.objects.filter(id=2).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=2).status))
        return redirect('flop', username)
    elif 'turn' in request.path:
        bet = GameWithPlayers.objects.get(
            game=game_data, action_preflop='Bet1'
        ).wage
        GameWithPlayers.objects.filter(
            player_user__username=username,
            game=game_data).update(
            action_preflop='Call',
            current_stack=F('current_stack') - bet,
            wage=bet
        )
        CurrentGame.objects.filter(id=game_data.id).update(
            bank=F('bank') + bet
        )
        PositionOfCurrentPlayer.objects.filter(id=2).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=2).status))
        return redirect('turn', username)
    else:
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
        elif position == 'BB':
            wage = 2 * game_data.big_blind
            GameWithPlayers.objects.filter(player_user__username=username,
                                           game=game_data).update(
                action_preflop='Call',
                current_stack=F('current_stack') - wage,
                wage=wage + game_data.small_blind
            )
            CurrentGame.objects.filter(id=game_data.id).update(
                bank=F('bank') + wage
            )
        PositionOfCurrentPlayer.objects.filter(id=1).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=1).status))
        return redirect('game', username)


def check(request, username):
    game_obj = CurrentGame.objects.last()
    GameWithPlayers.objects.filter(player_user__username=username,
                                   game=game_obj).update(
        action_preflop='Check')
    if 'flop' in request.path:
        PositionOfCurrentPlayer.objects.filter(id=2).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=2).status))
        return redirect('flop', username)
    elif 'turn' in request.path.__str__():
        PositionOfCurrentPlayer.objects.filter(id=2).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=2).status))
        return redirect('turn', username)
    else:
        PositionOfCurrentPlayer.objects.filter(id=1).update(
            status=change_position(
                PositionOfCurrentPlayer.objects.get(id=1).status))
        return redirect('game', username)


class FlopRound(TemplateView):
    template_name = 'game_flop.html'

    def get_context_data(self, **kwargs):
        context = super(FlopRound, self).get_context_data(**kwargs)
        flag = 0
        game_data = CurrentGame.objects.filter(
            user__username=self.args[0]).last()
        data = GameWithPlayers.objects.filter(
            game=game_data).all()
        actions_list = []

        for element in data:
            if element.action_preflop != 'Fold':
                actions_list.append(element.action_preflop)

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in data
        }

        seat_of_curr_pos = players_positions.get(
            PositionOfCurrentPlayer.objects.get(id=2).status)

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=seat_of_curr_pos
        )

        if actions_list.count('Check') == len(actions_list):
            flag = 1
            PositionOfCurrentPlayer.objects.filter(id=2).update(status='SB')
        elif 'Bet' in actions_list and len(actions_list) == 1:
            game_winner = GameWithPlayers.objects.get(
                action_preflop='Bet')
            if game_winner.player_bot:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=game_winner.current_player.bot_name)
            elif game_winner.player_user:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=game_winner.current_player.username)
        elif 'Bet' in actions_list and len(actions_list) > 1 and \
                actions_list.count('Check') == 0:
            flag = 1
            PositionOfCurrentPlayer.objects.filter(id=2).update(status='SB')

        context['data'] = data
        context['game_data'] = game_data
        context['seat'] = seat_of_curr_pos
        context['current_player'] = current_player
        context['flag'] = flag
        return context

    def post(self, request, username):
        game_data = CurrentGame.objects.filter(user__username=username).last()
        players = GameWithPlayers.objects.filter(game=game_data).all()
        bluff_index = random.randint(1, 7)

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in players
        }

        status = PositionOfCurrentPlayer.objects.get(id=2).status

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=players_positions.get(status)
        )
        if current_player.player_bot:
            current_combo = combination(
                current_player.handled_card_1 + current_player.handled_card_2,
                game_data.flop_1_card + game_data.flop_2_card +
                game_data.flop_3_card
            )

            if current_player.action_preflop.startswith('R'):
                if current_combo:
                    GameWithPlayers.objects.filter(
                        game=game_data, position=current_player.position
                    ).update(
                        action_preflop='Bet',
                        wage=game_data.bank * 0.6,
                        current_stack=F('current_stack') - F('wage')
                    )
                    CurrentGame.objects.filter(id=game_data.id).update(
                        bank=F('bank') + game_data.bank * 0.6
                    )
                else:
                    if bluff_index == 2 or bluff_index == 3 or bluff_index == 5:
                        GameWithPlayers.objects.filter(
                            game=game_data, position=current_player.position
                        ).update(action_preflop='Check')
                    else:
                        GameWithPlayers.objects.filter(
                            game=game_data, position=current_player.position
                        ).update(
                            action_preflop='Bet',
                            wage=game_data.bank * 0.6,
                            current_stack=F('current_stack') - F('wage')
                        )
                        CurrentGame.objects.filter(id=game_data.id).update(
                            bank=F('bank') + game_data.bank * 0.6
                        )
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status)
                )
            elif current_player.action_preflop.startswith('C'):
                if status == 'SB':
                    for element in players:
                        if element.action_preflop == 'Bet':
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=current_player.position
                            ).update(
                                action_preflop='Call',
                                wage=element.wage,
                                current_stack=F('current_stack') - F('wage')
                            )
                            CurrentGame.objects.filter(id=game_data.id).update(
                                bank=F('bank') + element.wage
                            )
                        else:
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=players_positions.get(status)
                            ).update(
                                action_preflop='Check'
                            )
                    PositionOfCurrentPlayer.objects.filter(id=2).update(
                        status=change_position(status))
                elif status == 'BB':
                    for element in players:
                        if element.action_preflop == 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=element.wage,
                                    current_stack=F('current_stack') - F('wage')
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Fold')
                        elif GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('SB')
                        ).action_preflop == 'Check' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('EP')
                                ).action_preflop == 'Fold' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('MP')
                                ).action_preflop == 'Fold' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('CO')
                                ).action_preflop == 'Fold' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('BU')
                                ).action_preflop == 'Fold':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Bet',
                                    wage=game_data.bank * 0.6,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + game_data.bank * 0.6
                                )
                            else:
                                if bluff_index in range(2, 5):
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=current_player.position
                                    ).update(
                                        action_preflop='Bet',
                                        wage=game_data.bank * 0.6,
                                        current_stack=F('current_stack') - F(
                                            'wage')
                                    )
                                    CurrentGame.objects.filter(
                                        id=game_data.id).update(
                                        bank=F('bank') + game_data.bank * 0.6
                                    )
                                else:
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Check'
                                    )
                        elif GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('SB')
                        ).action_preflop == 'Check' and \
                                element.action_preflop.startswith('R'):
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=players_positions.get(status)
                            ).update(
                                action_preflop='Check'
                            )
                    PositionOfCurrentPlayer.objects.filter(id=2).update(
                        status=change_position(status))
                elif status == 'EP':
                    for element in players:
                        if element.action_preflop == 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=element.wage,
                                    current_stack=F('current_stack') - F('wage')
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Fold')
                        PositionOfCurrentPlayer.objects.filter(id=2).update(
                            status=change_position(status))
                elif status == 'MP':
                    for element in players:
                        if element.action_preflop == 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=element.wage,
                                    current_stack=F('current_stack') - F('wage')
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Fold')
                        elif GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('EP')
                        ).action_preflop == 'Check':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Bet',
                                    wage=game_data.bank * 0.6,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + game_data.bank * 0.6
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Check')
                        PositionOfCurrentPlayer.objects.filter(id=2).update(
                            status=change_position(status))
                elif status == 'CO':
                    for element in players:
                        if element.action_preflop == 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=element.wage,
                                    current_stack=F('current_stack') - F('wage')
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Fold')
                        elif GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('EP')
                        ).action_preflop != 'Bet' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('MP')
                                ).action_preflop != 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Bet',
                                    wage=game_data.bank * 0.6,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + game_data.bank * 0.6
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Check')
                        PositionOfCurrentPlayer.objects.filter(id=2).update(
                            status=change_position(status))
                elif status == 'BU':
                    for element in players:
                        if element.action_preflop == 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Call',
                                    wage=element.wage,
                                    current_stack=F('current_stack') - F('wage')
                                )
                            else:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(action_preflop='Fold')
                        elif GameWithPlayers.objects.get(
                                game=game_data,
                                position=players_positions.get('EP')
                        ).action_preflop != 'Bet' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('MP')
                                ).action_preflop != 'Bet' and \
                                GameWithPlayers.objects.get(
                                    game=game_data,
                                    position=players_positions.get('CO')
                                ).action_preflop != 'Bet':
                            if current_combo:
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=current_player.position
                                ).update(
                                    action_preflop='Bet',
                                    wage=game_data.bank * 0.6,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=F('bank') + game_data.bank * 0.6
                                )
                            else:
                                if bluff_index in range(2, 6):
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=current_player.position
                                    ).update(
                                        action_preflop='Bet',
                                        wage=game_data.bank * 0.6,
                                        current_stack=F(
                                            'current_stack') - F('wage')
                                    )
                                    CurrentGame.objects.filter(
                                        id=game_data.id).update(
                                        bank=F('bank') + game_data.bank * 0.6
                                    )
                                else:
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=current_player.position
                                    ).update(action_preflop='Check')
                        PositionOfCurrentPlayer.objects.filter(id=2).update(
                            status=change_position(status))
            else:
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status)
                )
        else:
            if current_player.action_preflop == 'Fold':
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status)
                )
            else:
                GameWithPlayers.objects.filter(
                    player_user__username=username).update(
                    action_preflop='Bet',
                    wage=request.POST.get('raise_number'),
                    current_stack=F('current_stack') - F('wage')
                )
                CurrentGame.objects.filter(id=game_data.id).update(
                    bank=F('bank') + request.POST.get('raise_number')
                )
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status)
                )

        return redirect('flop', username)


class TurnRound(TemplateView):
    template_name = 'game_turn.html'

    def get_context_data(self, **kwargs):
        context = super(TurnRound, self).get_context_data(**kwargs)
        flag = 0
        game_data = CurrentGame.objects.last()
        data = GameWithPlayers.objects.filter(
            game=game_data).all()
        actions_list = []

        for element in data:
            if element.action_preflop != 'Fold':
                actions_list.append(element.action_preflop)

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in data
        }

        seat_of_curr_pos = players_positions.get(
            PositionOfCurrentPlayer.objects.get(id=2).status)

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=seat_of_curr_pos
        )

        if actions_list.count('Check1') == len(actions_list):
            flag = 1
        elif 'Bet1' in actions_list and len(actions_list) == 1:
            flag = 2
            game_winner = GameWithPlayers.objects.get(
                action_preflop='Bet1',
                game=game_data)
            if game_winner.player_bot:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=game_winner.current_player.bot_name)
            elif game_winner.player_user:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=game_winner.current_player.username)
        elif 'Bet1' in actions_list and len(actions_list) > 1 and \
                actions_list.count('Check1') == 0 and \
                actions_list.count('Check') == 0:
            flag = 1
            PositionOfCurrentPlayer.objects.filter(id=2).update(status='SB')

        context['data'] = data
        context['game_data'] = game_data
        context['seat'] = seat_of_curr_pos
        context['current_player'] = current_player
        context['flag'] = flag
        return context

    def post(self, request, username):
        bluff_index = random.randint(1, 5)
        game_data = CurrentGame.objects.filter(user__username=username).last()
        players = GameWithPlayers.objects.filter(game=game_data).all()
        actions = [pl.action_preflop for pl in players]

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in players
        }

        status = PositionOfCurrentPlayer.objects.get(id=2).status

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=players_positions.get(status)
        )
        if current_player.player_bot:
            current_combo = combination(
                current_player.handled_card_1 + current_player.handled_card_2,
                game_data.flop_1_card + game_data.flop_2_card +
                game_data.flop_3_card + game_data.turn
            )
            if current_player.action_preflop == 'Bet':
                GameWithPlayers.objects.filter(
                    game=game_data, position=current_player.position
                ).update(
                    action_preflop='Bet1',
                    wage=game_data.bank * 0.55,
                    current_stack=F('current_stack') - F('wage')
                )
                CurrentGame.objects.filter(id=game_data.id).update(
                    bank=game_data.bank + game_data.bank * 0.55
                )
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status))

            elif current_player.action_preflop.startswith('C'):
                if current_player.action_preflop == 'Call':
                    GameWithPlayers.objects.filter(
                        game=game_data,
                        position=players_positions.get(status)
                    ).update(
                        action_preflop='Check1',
                    )
                for elem in players:
                    if elem.action_preflop == 'Bet1' and \
                            current_player.action_preflop == 'Check1':
                        if current_combo:
                            bet1 = GameWithPlayers.objects.get(
                                game=game_data,
                                action_preflop='Bet1'
                            ).wage
                            pot1 = game_data.bank + bet1
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=players_positions.get(status)
                            ).update(
                                action_preflop='Call',
                                wage=bet1,
                                current_stack=F('current_stack') - F('wage')
                            )
                            CurrentGame.objects.filter(id=game_data.id).update(
                                bank=pot1
                            )
                        else:
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=players_positions.get(status)
                            ).update(
                                action_preflop='Fold',
                            )
                    elif actions.count(
                            'Bet1') == 0 and actions.count('Bet') == 0:
                        if current_combo:
                            if current_combo != 'pair' or current_combo != 'FD':
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=players_positions.get(status)
                                ).update(
                                    action_preflop='Bet1',
                                    wage=game_data.bank * 0.55,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=game_data.bank + game_data.bank * 0.55
                                )
                            elif current_combo == 'pair':
                                if bluff_index in range(1, 4):
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Bet1',
                                        wage=game_data.bank * 0.55,
                                        current_stack=F('current_stack') - F(
                                            'wage')
                                    )
                                    CurrentGame.objects.filter(
                                        id=game_data.id).update(
                                        bank=F('bank') + game_data.bank * 0.55
                                    )
                                else:
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Check1',
                                    )
                            elif current_combo == 'FD':
                                if bluff_index in range(3, 5):
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Bet1',
                                        wage=game_data.bank * 0.55,
                                        current_stack=F('current_stack') - F(
                                            'wage')
                                    )
                                    CurrentGame.objects.filter(
                                        id=game_data.id).update(
                                        bank=F('bank') + game_data.bank * 0.55
                                    )
                                else:
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Check1',
                                    )
                    PositionOfCurrentPlayer.objects.filter(id=2).update(
                        status=change_position(status))

            elif current_player.action_preflop == 'Fold':
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status))
        else:
            if current_player.action_preflop == 'Fold':
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status))
            else:
                GameWithPlayers.objects.filter(
                    player_user__username=username).update(
                    action_preflop='Bet1',
                    wage=request.POST.get('raise_number'),
                    current_stack=F('current_stack') - F('wage')
                )
                CurrentGame.objects.filter(id=game_data.id).update(
                    bank=F('bank') + request.POST.get('raise_number')
                )
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status)
                )

        return redirect('turn', username)


class RiverRound(TemplateView):
    template_name = 'game_river.html'

    def get_context_data(self, **kwargs):
        context = super(RiverRound, self).get_context_data(**kwargs)
        flag = 0
        game_data = CurrentGame.objects.filter(
            user__username=self.args[0]).last()
        data = GameWithPlayers.objects.filter(game=game_data).all()
        actions_list = []

        for element in data:
            if element.action_preflop != 'Fold':
                actions_list.append(element.action_preflop)

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in data
        }

        seat_of_curr_pos = players_positions.get(
            PositionOfCurrentPlayer.objects.get(id=2).status)

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=seat_of_curr_pos
        )

        if actions_list.count('Check2') == len(actions_list):
            flag = 1
        elif 'Bet2' in actions_list and len(actions_list) == 1:
            flag = 2
            game_winner = GameWithPlayers.objects.get(
                action_preflop='Bet2',
                game=game_data)
            if game_winner.player_bot:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=game_winner.current_player.bot_name)
            elif game_winner.player_user:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=game_winner.current_player.username)
        elif 'Bet2' in actions_list and len(actions_list) > 1 and \
                actions_list.count('Check2') == 0 and \
                actions_list.count('Check1') == 0:
            flag = 1

        context['data'] = data
        context['game_data'] = game_data
        context['seat'] = seat_of_curr_pos
        context['current_player'] = current_player
        context['flag'] = flag
        return context

    def post(self, request, username):
        bluff_index = random.randint(1, 5)
        game_data = CurrentGame.objects.filter(user__username=username).last()
        players = GameWithPlayers.objects.filter(game=game_data).all()
        actions = [pl.action_preflop for pl in players]

        players_positions = {
            current_player_position(
                player.position, game_data.big_blind_seat,
                game_data.small_blind_seat): player.position
            for player in players
        }

        status = PositionOfCurrentPlayer.objects.get(id=2).status

        current_player = GameWithPlayers.objects.get(
            game=game_data, position=players_positions.get(status)
        )
        if current_player.player_bot:
            current_combo = combination(
                current_player.handled_card_1 + current_player.handled_card_2,
                game_data.flop_1_card + game_data.flop_2_card +
                game_data.flop_3_card + game_data.turn
            )
            if current_player.action_preflop == 'Bet1':
                GameWithPlayers.objects.filter(
                    game=game_data, position=current_player.position
                ).update(
                    action_preflop='Bet2',
                    wage=game_data.bank * 0.55,
                    current_stack=F('current_stack') - F('wage')
                )
                CurrentGame.objects.filter(id=game_data.id).update(
                    bank=F('bank') + game_data.bank * 0.55
                )
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status))

            elif current_player.action_preflop.startswith('C'):
                if current_player.action_preflop == 'Call':
                    GameWithPlayers.objects.filter(
                        game=game_data,
                        position=players_positions.get(status)
                    ).update(
                        action_preflop='Check2',
                    )
                for elem in players:
                    if elem.action_preflop == 'Bet2' and \
                            current_player.action_preflop == 'Check2':
                        if current_combo:
                            bet3 = GameWithPlayers.objects.get(
                                game=game_data,
                                action_preflop='Bet2'
                            ).wage
                            pot3 = game_data.bank + bet3
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=players_positions.get(status)
                            ).update(
                                action_preflop='Call',
                                wage=bet3,
                                current_stack=F('current_stack') - F('wage')
                            )
                            CurrentGame.objects.filter(id=game_data.id).update(
                                bank=pot3
                            )
                        else:
                            GameWithPlayers.objects.filter(
                                game=game_data,
                                position=players_positions.get(status)
                            ).update(
                                action_preflop='Fold',
                            )
                    elif actions.count(
                            'Bet1') == 0 and actions.count('Bet2') == 0:
                        if current_combo:
                            if current_combo != 'pair' or current_combo != 'FD':
                                GameWithPlayers.objects.filter(
                                    game=game_data,
                                    position=players_positions.get(status)
                                ).update(
                                    action_preflop='Bet2',
                                    wage=game_data.bank * 0.55,
                                    current_stack=F('current_stack') - F('wage')
                                )
                                CurrentGame.objects.filter(
                                    id=game_data.id).update(
                                    bank=game_data.bank * 0.55 + game_data.bank
                                )
                            elif current_combo == 'pair':
                                if bluff_index in range(1, 4):
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Bet2',
                                        wage=game_data.bank * 0.55,
                                        current_stack=F('current_stack') - F(
                                            'wage')
                                    )
                                    CurrentGame.objects.filter(
                                        id=game_data.id).update(
                                        bank=F('bank') + game_data.bank * 0.55
                                    )
                                else:
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Check2',
                                    )
                            elif current_combo == 'FD':
                                if bluff_index in range(3, 5):
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Bet2',
                                        wage=game_data.bank * 0.55,
                                        current_stack=F('current_stack') - F(
                                            'wage')
                                    )
                                    CurrentGame.objects.filter(
                                        id=game_data.id).update(
                                        bank=F('bank') + game_data.bank * 0.55
                                    )
                                else:
                                    GameWithPlayers.objects.filter(
                                        game=game_data,
                                        position=players_positions.get(status)
                                    ).update(
                                        action_preflop='Check2',
                                    )
                    PositionOfCurrentPlayer.objects.filter(id=2).update(
                        status=change_position(status))

            elif current_player.action_preflop == 'Fold':
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status))
        else:
            if current_player.action_preflop == 'Fold':
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status))
            else:
                GameWithPlayers.objects.filter(
                    player_user__username=username).update(
                    action_preflop='Bet2',
                    wage=request.POST.get('raise_number'),
                    current_stack=F('current_stack') - F('wage')
                )
                CurrentGame.objects.filter(id=game_data.id).update(
                    bank=F('bank') + request.POST.get('raise_number')
                )
                PositionOfCurrentPlayer.objects.filter(id=2).update(
                    status=change_position(status)
                )

        return redirect('river', username)


class ShowDown(TemplateView):
    template_name = 'showdown.html'

    dict_hand = {
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        'T': 10,
        'J': 11,
        'Q': 12,
        'K': 13,
        'A': 14,
    }
    dict_combos = {
        'flush royal': 10,
        'street flush': 9,
        'quad': 8,
        'full house': 7,
        'flush': 6,
        'street': 5,
        'set': 4,
        'three of kind': 3,
        'two pair': 2,
        'pair': 1,
        'FD': 0,
        None: 0
    }

    def get_context_data(self, **kwargs):
        context = super(ShowDown, self).get_context_data(**kwargs)
        game_data = CurrentGame.objects.filter(
            user__username=self.args[0]).last()
        data = GameWithPlayers.objects.filter(
            Q(game=game_data, action_preflop='Bet2') |
            Q(game=game_data, action_preflop__startswith='C')).all()

        dct_of_pos_and_combos_value = {
            elem.position: self.dict_combos.get(
                combination(
                    elem.handled_card_1 + elem.handled_card_2,
                    game_data.flop_1_card + game_data.flop_2_card +
                    game_data.flop_3_card + game_data.turn
                )
            )
            for elem in data
        }

        list_of_pos = [
            pos for pos, combs_value in dct_of_pos_and_combos_value.items() if
            combs_value == max(
                [_ for _ in dct_of_pos_and_combos_value.values()]
            )
        ]

        if len(list_of_pos) == 1:
            if GameWithPlayers.objects.get(position=list_of_pos[0]).player_bot:
                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=GameWithPlayers.objects.get(
                        position=list_of_pos[0]).player_bot.bot_name
                )
            else:

                CurrentGame.objects.filter(id=game_data.id).update(
                    winner=GameWithPlayers.objects.get(
                        position=list_of_pos[0]).player_user.username
                )
                GameWithPlayers.objects.filter(
                    position=list_of_pos[0]
                ).update(
                    player_user__balance=CustomUser.objects.get(
                        user_player__position=list_of_pos[
                            0]).balance + game_data.bank
                )
        elif len(list_of_pos) > 1:
            if dct_of_pos_and_combos_value.get(list_of_pos[0]) != 6 and \
                    dct_of_pos_and_combos_value.get(list_of_pos[0]) != 7:
                pos_handled_cards = {player.position: [
                    player.handled_card_1[1], player.handled_card_2[1]
                ] for player in data if player.position in list_of_pos}

                deck = (
                               game_data.flop_1_card + game_data.flop_2_card +
                               game_data.flop_3_card + game_data.turn + game_data.river
                       )[1::2]

                for elem in pos_handled_cards.values():
                    for sec in deck:
                        elem.append(sec)

                for lst in pos_handled_cards.values():
                    for _ in range(len(lst)):
                        lst[_] = self.dict_hand.get(lst[_])

                winner_pos = [
                    pos for pos in pos_handled_cards if sum(
                        pos_handled_cards.get(pos)
                    ) == max(
                        [sum(value) for value in pos_handled_cards.values()])
                ]

                if GameWithPlayers.objects.get(
                        position=winner_pos[0]).player_bot:
                    CurrentGame.objects.filter(id=game_data.id).update(
                        winner=GameWithPlayers.objects.get(
                            position=winner_pos[0]).player_bot.bot_name
                    )
                else:

                    CurrentGame.objects.filter(id=game_data.id).update(
                        winner=GameWithPlayers.objects.get(
                            position=winner_pos[0]).player_user.username
                    )
                    GameWithPlayers.objects.filter(
                        position=winner_pos[0]
                    ).update(
                        player_user__balance=CustomUser.objects.get(
                            user_player__position=winner_pos[
                                0]).balance + game_data.bank
                    )
            elif dct_of_pos_and_combos_value.get(list_of_pos[0]) == 6:
                pass

        context['data'] = data
        context['game_data'] = game_data
        return context
