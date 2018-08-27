from io import BytesIO
from django.core.files import File
from collections import Counter


def upload_file(file):
    buffer = BytesIO()
    for chunk in file.chunks():
        buffer.write(chunk)
    return File(buffer)


def most_common(lst):
    data = Counter(lst)
    return data.most_common(1)[0]


def convert_to_nums(h, nums={'T': 10, 'J': 11, 'Q': 12, 'K': 13, "A": 14}):
    for x in range(len(h)):

        if (h[x][1]) in nums.keys():
            h[x] = h[x][0] + str(nums.get(h[x][1]))

    return h


def is_royal(h):
    nh = convert_to_nums(h)
    if is_seq(h):
        if is_flush(h):
            nn = [int(x[1:]) for x in nh]
            if min(nn) == 10:
                return True

    else:
        return False


def is_seq(h):
    ace = False
    r = h[:]
    h = [x[1:] for x in convert_to_nums(h)]
    h = [int(x) for x in h]
    h = list(sorted(h))
    list_of_straights = [h[i:i + 5] for i in range(len(h) - 4) if
                         h[i:i + 5] == [s for s in range(h[i], h[i] + 5)]]
    if len(list_of_straights) > 1:
        return True, list_of_straights[len(list_of_straights) - 1]

    aces = [i for i in h if str(i) == "14"]
    if len(aces) == 1:
        for x in range(len(h)):
            if str(h[x]) == "14":
                h[x] = 1

    h = list(sorted(h))
    list_of_straights_2 = [h[i:i + 5] for i in range(len(h) - 4) if
                           h[i:i + 5] == [s for s in range(h[i], h[i] + 5)]]
    if len(list_of_straights_2) > 1:
        return True, list_of_straights[len(list_of_straights_2) - 1]


def is_flush(h):
    suits = [x[:1] for x in h]
    s = most_common(suits)
    if s[1] >= 5:
        return True, h
    else:
        return False


def is_four_of_a_kind(h):
    h = [a[1:] for a in h]
    i = most_common(h)
    if i[1] == 4:
        return True, i[0]
    else:
        return False


def is_three_of_a_kind(h):
    h = [a[1:] for a in h]
    i = most_common(h)
    if i[1] == 3:
        return True, i[0]
    else:
        return False


def is_full_house(h):
    h = [a[1:] for a in h]
    data = Counter(h)
    a, b = data.most_common(1)[0], data.most_common(2)[-1]
    if str(a[1]) == '3' and str(b[1]) == '2':
        return True, (a, b)
    return False


def is_two_pair(h):
    h = [a[1:] for a in h]
    data = Counter(h)
    a, b = data.most_common(1)[0], data.most_common(2)[-1]
    if str(a[1]) == '2' and str(b[1]) == '2':
        return True, (a[0], b[0])
    return False


def is_pair(h):
    h = [a[1:] for a in h]
    data = Counter(h)
    a = data.most_common(1)[0]

    if str(a[1]) == '2':
        return True, (a[0])
    else:
        return False


# get the high card
def get_high(h):
    return list(sorted([int(x[1:]) for x in convert_to_nums(h)], reverse=True))[
        0]


# FOR HIGH CARD or ties, this function compares two hands by ordering the hands from highest to lowest and comparing each card and returning when one is higher then the other
# def compare(array):
#     xs, ys = list(sorted(xs, reverse=True)), list(sorted(ys, reverse=True))
#
#     for i, c in enumerate(xs):
#         if ys[i] > c:
#             return 'RIGHT'
#         elif ys[i] < c:
#             return 'LEFT'
#
#     return "TIE"


def evaluate_hand(h):
    if is_royal(h):
        return "ROYAL FLUSH", h, 10
    elif is_seq(h) and is_flush(h):
        return "STRAIGHT FLUSH", h, 9
    elif is_four_of_a_kind(h):
        _, fourofakind = is_four_of_a_kind(h)
        return "FOUR OF A KIND", fourofakind, 8
    elif is_full_house(h):
        return "FULL HOUSE", h, 7
    elif is_flush(h):
        _, flush = is_flush(h)
        return "FLUSH", h, 6
    elif is_seq(h):
        _, seq = is_seq(h)
        return "STRAIGHT", h, 5
    elif is_three_of_a_kind(h):
        _, threeofakind = is_three_of_a_kind(h)
        return "THREE OF A KIND", threeofakind, 4
    elif is_two_pair(h):
        _, two_pair = is_two_pair(h)
        return "TWO PAIR", two_pair, 3
    elif is_pair(h):
        _, pair = is_pair(h)
        return "PAIR", pair, 2
    else:
        return "HIGH CARD", h, 1


def compare_hands(hands):
    list_of_combs = [evaluate_hand(hand) for hand in hands.values()]

    if list_of_combs[0][0] == "STRAIGHT FLUSH":

        st_dict = {
            ps: [is_seq(hand)] for ps, hand in hands.items()
        }

        wp = [
            pos for pos, vl in st_dict.items() if st_dict[pos][1] == max(vl[1])
        ]
        return wp[0]

    elif list_of_combs[0][0] == "PAIR":
        wp = [
            pos for pos, combs_value in hands.items() if
            int(combs_value[1]) == max([int(_[1]) for _ in hands.values()])
        ]
        if len(wp) > 1:
            compare_dict = {
                pos: [int(x[1:]) for x in hands.get(pos)] for pos in wp}

            for lst in compare_dict.values():
                for index in range(len(lst[2:])):
                    if lst[1] and lst[2] < (lst[2:])[index]:
                        return 'Draw'
                    else:
                        for elem in lst:
                            if lst.count(elem) == 2:
                                lst.remove(elem)

                        pos_lst = [
                            key for key in compare_dict if
                            compare_dict.get(key)[0] == max([
                                x[0] for x in compare_dict.values()])
                        ]
                        return pos_lst[0]
        return wp[0]

    elif list_of_combs[0][0] == "FLUSH":

        suit = [
            s for s in ''.join(
                hands.values[0]) if ''.join(hands.values[0]).count(s) >= 5][0]

        deck = [va for va in hands.values()][0][2:]

        deck = [int(a[1:]) for a in deck if a.startswith(suit)]

        compare_dict = {
            pos: [
                int(x[1:]) for x in hands.get(pos) if x.startswith(suit)
            ] for pos in hands
        }

        for element in compare_dict.values():
            if len(deck) == 5:
                for ind in range(len(deck)):
                    if element[0] and element[1] < deck[ind]:
                        return 'Draw'
                    else:
                        pos_win = [
                            kp for kp in compare_dict if max(
                                compare_dict.get(kp)[:2]
                            ) == max([val[:2] for val in compare_dict.values()])
                        ]
                        return pos_win[0]
            elif len(deck) < 5:
                lst_1 = [
                    [
                        int(xd[1:]) for xd in data_s[:2] if xd.startswith(suit)
                    ] for data_s in hands.values()
                ]
                wp = [
                    p for p in compare_dict if max(
                        max(lst_1)) in compare_dict.get(p)
                ]
                return wp[0]

    elif list_of_combs[0][0] == 'STRAIGHT':

        st_dict = {
            ps: [is_seq(hand)] for ps, hand in hands.items()
        }

        tst_lst = [vl[1] for vl in st_dict.values()]

        if tst_lst.count(max(tst_lst)) == len(tst_lst):
            return 'Draw'

        wp = [
            pos for pos, vl in st_dict.items() if st_dict[pos][1] == max(vl[1])
        ]
        return wp[0]

    elif list_of_combs[0][0] == 'FULL HOUSE':

        winner_pos = [
            pos for pos in hands if list(
                set([i for i in hands.get(pos) if
                     hands.get(pos).count(i) == 3])
            ) == max(
                [
                    list(
                        set(
                            [
                                elem for elem in val if
                                val.count(elem) == 3
                            ]
                        )
                    ) for
                    val in hands.values()
                ]
            )
        ]
        if len(winner_pos) > 1:
            return 'Draw'

        return winner_pos[0]
#
#         fh1, fh2 = int(is_fullhouse(h1)[1][0][0]), int(
#             is_fullhouse(h2)[1][0][0])
#         if fh1 > fh2:
#             return "left", one[0], one[1]
#         else:
#             return "right", two[0], two[1]
#     elif one[0] == "HIGH CARD":
#         sett1, sett2 = convert_tonums(h1), convert_tonums(h2)
#         sett1, sett2 = [int(x[:-1]) for x in sett1], [int(x[:-1]) for x in
#                                                       sett2]
#         com = compare(sett1, sett2)
#         if com == "TIE":
#             return "none", one[1], two[1]
#         elif com == "RIGHT":
#             return "right", two[0], two[1]
#         else:
#             return "left", one[0], one[1]
#
#     elif len(one[1]) < 5:
#         if max(one[1]) == max(two[1]):
#             return "none", one[1], two[1]
#         elif max(one[1]) > max(two[1]):
#             return "left", one[0], one[1]
#         else:
#             return "right", two[0], two[1]
#     else:
#         n_one, n_two = convert_tonums(one[1]), convert_tonums(two[1])
#         n_one, n_two = [int(x[:-1]) for x in n_one], [int(x[:-1]) for x in
#                                                       n_two]
#
#         if max(n_one) == max(n_two):
#             return "none", one[1], two[1]
#         elif max(n_one) > max(n_two):
#             return "left", one[0], one[1]
#         else:
#             return "right", two[0], two[1]
#
#
#
