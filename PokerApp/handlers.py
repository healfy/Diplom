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
        return 'EP'


def combination(hand, deck):
    streets = [
        'A2345', '23456', '34567', '45678', '56789', '6789T', '789TJ',
        '89TJQ', '9TJQK', 'TJQKA',
    ]
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
    if hand[1] == hand[3] and deck.count(hand[1]) == 1:
        return 'set'
    elif hand[1] == hand[3] and deck.count(hand[1]) == 2:
        return 'quad'
    elif hand[0] == hand[2] and deck.count(hand[0]) >= 3:
        return 'flash'
    elif deck.count(hand[1]) == 3 and hand[1] != hand[3] or \
            deck.count(hand[3]) == 3 and hand[3] != hand[1]:
        return 'quad'
    elif hand[1] != hand[3] and deck.count(hand[1]) == 1 or \
            deck.count(hand[3]) == 1:
        return 'pair'
    elif hand[1] == hand[3] and deck.count(hand[1]) == 0:
        return 'pair'
    elif hand[1] != hand[3] and deck.count(hand[1]) == 1 and \
            deck.count(hand[3]) == 1:
        return 'two pair'
    elif hand[1] == hand[3] and deck.count(hand[1]) == 1 and \
        deck.count(deck[1]) == 3 or deck.count(deck[3]) == 3 or \
            deck.count(deck[5]) == 3 or deck.count(deck[7]) == 3 or \
            deck.count(deck[9]) == 3:
        return 'full house'
    elif hand[1] != hand[3] and deck.count(hand[1]) == 1 or \
            deck.count(hand[3]) == 1 and deck.count(deck[1]) == 3 \
            or deck.count(deck[3]) == 3 or deck.count(deck[5]) == 3:
        return 'full house'
    elif hand[1] != hand[3] and deck.count(hand[1]) == 2 and \
            deck.count(hand[3]) == 1 or deck.count(hand[1]) == 1 and \
            deck.count(hand[3]) == 2:
        return 'full house'
    elif hand[1] != hand[3] and deck.count(hand[1]) == 2 or \
            deck.count(hand[3]) == 2:
        return ' three or kind'
