def preflop_actions(list_of_actions):
    if len(list_of_actions) == 6:
        return True
    return False


def hand_power(card1, card2, position):
    rank_ep = ['A', 'K', 'Q', 'J', 'T']
    hand = card1 + card2
    if position == 'EP':
        if hand[1] == hand[3]:
            return True
        elif hand[1] in rank_ep and hand[3] in rank_ep:
            return True

    return False
