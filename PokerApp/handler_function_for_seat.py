def current_player_position(seat, bb_seat, sb_seat):
    if bb_seat == 2:
        if seat == 3:
            position = 'EP'
            return position
        elif seat == 4:
            position = 'MP'
            return position
        elif seat == 5:
            position = 'CO'
            return position
        elif seat == 6:
            position = 'BU'
            return position
        elif seat == bb_seat:
            position = 'BB'
            return position
        elif seat == sb_seat:
            position = 'SB'
            return position
    elif bb_seat == 3:
        if seat == 4:
            position = 'EP'
            return position
        elif seat == 5:
            position = 'MP'
            return position
        elif seat == 6:
            position = 'CO'
            return position
        elif seat == 1:
            position = 'BU'
            return position
        elif seat == bb_seat:
            position = 'BB'
            return position
        elif seat == sb_seat:
            position = 'SB'
            return position
    elif bb_seat == 4:
        if seat == 5:
            position = 'EP'
            return position
        elif seat == 6:
            position = 'MP'
            return position
        elif seat == 1:
            position = 'CO'
            return position
        elif seat == 2:
            position = 'BU'
            return position
        elif seat == bb_seat:
            position = 'BB'
            return position
        elif seat == sb_seat:
            position = 'SB'
            return position
    elif bb_seat == 5:
        if seat == 6:
            position = 'EP'
            return position
        elif seat == 1:
            position = 'MP'
            return position
        elif seat == 2:
            position = 'CO'
            return position
        elif seat == 3:
            position = 'BU'
            return position
        elif seat == bb_seat:
            position = 'BB'
            return position
        elif seat == sb_seat:
            position = 'SB'
            return position
    elif bb_seat == 6:
        if seat == 1:
            position = 'EP'
            return position
        elif seat == 2:
            position = 'MP'
            return position
        elif seat == 3:
            position = 'CO'
            return position
        elif seat == 4:
            position = 'BU'
            return position
        elif seat == bb_seat:
            position = 'BB'
            return position
        elif seat == sb_seat:
            position = 'SB'
            return position
    elif bb_seat == 1:
        if seat == 2:
            position = 'EP'
            return position
        elif seat == 3:
            position = 'MP'
            return position
        elif seat == 4:
            position = 'CO'
            return position
        elif seat == 5:
            position = 'BU'
            return position
        elif seat == bb_seat:
            position = 'BB'
            return position
        elif seat == sb_seat:
            position = 'SB'
            return position
