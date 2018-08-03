def preflop_actions(list_of_actions):
    if None in list_of_actions:
        return False
    return True


def hand_power(card1, card2, position):
    premium_rank = ['A', 'K', 'Q', 'J', 'T']
    middle_rank = ['9', '8', '7']
    hand = card1 + card2
    if position == 'EP':
        if hand[1] == hand[3]:
            return True,
        elif hand[1] in premium_rank and hand[3] in premium_rank:
            return True
    elif position == 'MP':
        if hand[1] == hand[3]:
            return True
        elif hand[1] in premium_rank and hand[3] in premium_rank:
            return True
        elif hand[0] == hand[2] and hand[1] in middle_rank and hand[3] \
                in middle_rank:
            return True
    elif position == 'CO':
        if hand[1] == hand[3]:
            return True
        elif hand[1] in premium_rank and hand[3] in premium_rank:
            return True
        elif hand[0] == hand[2] and hand[1] in middle_rank and hand[3] \
                in middle_rank:
            return True
    elif position == 'BU':
        if hand[1] == hand[3]:
            return True
        elif hand[1] in premium_rank and hand[3] in premium_rank:
            return True
        elif hand[1] in premium_rank and hand[3] in middle_rank or hand[1] \
                in middle_rank and hand[3] in premium_rank:
            return True
    elif position == 'SB':
        return True
    elif position == 'BB':
        return True
    return False


def change_position(obj):
    if obj == 'EP':
        return 'MP'
    elif obj == 'MP':
        return 'CO'
    elif obj == 'CO':
        return 'BU'
    elif obj == 'BU':
        return 'SB'
    elif obj == 'SB':
        return 'BB'
    elif obj == 'BB':
        return 'SB'
