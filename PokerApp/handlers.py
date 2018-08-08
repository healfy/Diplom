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
        [14, 2, 3, 4, 5], [2, 3, 4, 5, 6], [3, 4, 5, 6, 7], [4, 5, 6, 7, 8],
        [5, 6, 7, 8, 9], [6, 7, 8, 9, 10], [7, 8, 9, 10, 11],
        [8, 9, 10, 11, 12], [9, 10, 11, 12, 13], [10, 11, 12, 13, 14]
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
    array = list(set(
        [dict_hand.get(_) for _ in ''.join(sorted((hand + deck)[1::2]))]))

    section = deck[1::2]

    for element in section:
        if hand[1] == hand[3] and deck.count(hand[1]) == 1 and \
                section.count(element) == 1:
            return 'set'
        elif section.count(element) == 4:
            return 'quad'
        elif hand[1] == hand[3] and deck.count(hand[1]) == 2:
            return 'quad'
        elif hand[0] == hand[2] and deck.count(hand[0]) >= 3:
            return 'flash'
        elif hand[1] == hand[3] and deck.count(hand[1]) == 0 and \
                section.count(element) == 1:
            return 'pair'
        elif hand[1] == hand[3] and section.count(element) == 2 and \
                deck.count(hand[1]) == 0:
            return 'two pair'
        elif hand[1] == hand[3] and deck.count(hand[1]) == 1 and \
                section.count(element) == 2:
            return 'full house'
        elif hand[1] == hand[3] and deck.count(hand[1]) == 0 and \
                section.count(element) == 3:
            return 'full house'
        elif hand[1] != hand[3]:
            if deck.count(hand[3]) == 1 and deck.count(hand[1]) == 0 or \
                    deck.count(hand[1]) == 1 and deck.count(hand[3]) == 0:
                if section.count(element) == 1:
                    return 'pair'
            elif deck.count(hand[1]) == 1 and deck.count(hand[3]) == 1:
                if section.count(element) == 1:
                    return 'two pair'
            elif deck.count(hand[1]) == 3 or deck.count(hand[3]) == 3:
                return 'quad'
            elif deck.count(hand[1]) == 0 and deck.count(hand[3]) == 0:
                if deck.count(hand[0]) < 2 and deck.count(hand[2]) < 2:
                    if section.count(element) == 1:
                        for street in streets:
                            if ''.join(['{}'.format(_) for _ in array]).count(
                                    ''.join(
                                        ['{}'.format(_) for _ in street])) != 0:
                                return 'street'
                            else:
                                return None
            elif deck.count(hand[1]) == 1 and deck.count(hand[3]) == 0 or \
                    deck.count(hand[3]) == 1 and deck.count(hand[1]) == 0:
                if section.count(element) == 3:
                    return 'full house'
            elif deck.count(hand[1]) == 2 and deck.count(hand[3]) == 0 or \
                    deck.count(hand[3]) == 2 and deck.count(hand[1]) == 0:
                return 'three of kind'
            elif deck.count(hand[1]) == 2 and deck.count(hand[3]) == 1 or \
                    deck.count(hand[1]) == 1 and deck.count(hand[3]) == 2:
                return 'full house'
