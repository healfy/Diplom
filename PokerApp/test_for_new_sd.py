from PokerApp.models import *
from PokerApp.utills import evaluate_hand
from django.db.models import Q

game_data = CurrentGame.objects.filter(
            user__username='healfy').last()
data = GameWithPlayers.objects.filter(
    Q(game=game_data, action_preflop='Bet2') |
    Q(game=game_data, action_preflop__startswith='C')).all()

dct = {player.position: [
                    player.handled_card_1, player.handled_card_2,
                    game_data.flop_1_card, game_data.flop_2_card,
                    game_data.flop_3_card, game_data.turn, game_data.river
                ] for player in data}
dct_of_combs = {
    pos: evaluate_hand(val) for pos, val in dct.items()
}

list_of_pos = [
            pos for pos, combs_value in dct_of_combs.items() if
            combs_value[2] == max([_[2] for _ in dct_of_combs.values()])
        ]
