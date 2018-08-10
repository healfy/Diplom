from PokerApp.handler_function_for_seat import current_player_position
from PokerApp.models import CurrentGame, GameWithPlayers
from PokerApp.handlers import *


game_object = CurrentGame.objects.last()

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
        game=game_object, player_user__username='healfy').position,
    game_object.big_blind_seat,
    game_object.small_blind_seat)] = GameWithPlayers.objects.get(
        game=game_object, player_user__username='healfy'
).current_player.username


hand_power_and_positions = {
    player.current_player.bot_name: [hand_power(
        GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_1,
        GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_2,
        current_player_position(
            player.position, game_object.big_blind_seat,
            game_object.small_blind_seat)),
        current_player_position(
            player.position, game_object.big_blind_seat,
            game_object.small_blind_seat),
        GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_1
        + GameWithPlayers.objects.get(
            game=game_object,
            player_bot__bot_name=player.current_player.bot_name).handled_card_2
    ] for player in players_bot
}

