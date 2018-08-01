from PokerApp.handler_function_for_seat import bot_player_position
from PokerApp.models import CurrentGame, GameWithPlayers
from PokerApp.handlers import *


game_object = CurrentGame.objects.last()

players = [
    GameWithPlayers.objects.get(
                game=game_object, player_bot_id=i) for i in range(1, 6)
]

hand_power_and_positions = {
    player.current_player.bot_name: [hand_power(
        GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_1,
        GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_2,
        bot_player_position(
            player.position, game_object.big_blind_seat,
            game_object.small_blind_seat)),
        bot_player_position(
            player.position, game_object.big_blind_seat,
            game_object.small_blind_seat),
        GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_1
        + GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_2
    ] for player in players
}
