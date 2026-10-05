"""Unabhängiges Orakel für die Zirkelmethode.

Rechenweg des Orakels: nicht die Rotation mit Schrittweite, sondern die
Summenregel der Berger-Tafeln. In Runde t (0-indiziert) treffen sich zwei
Spieler a, b der rotierenden Gruppe genau dann, wenn a + b = t + 2 (mod m);
der Spieler mit 2a = t + 2 (mod m) bekommt den Fixspieler (bzw. das Freilos).
Dazu die veröffentlichte FIDE-Tafel für 9/10 Spieler (Paarungen und Farben,
Runde für Runde) und Zählungen per Vollaufzählung der Spielerpaare.
"""

from __future__ import annotations

import pytest

from rr_scheduler import generate_schedule

FIDE_TABLE_10 = [
    [(1, 10), (2, 9), (3, 8), (4, 7), (5, 6)],
    [(10, 6), (7, 5), (8, 4), (9, 3), (1, 2)],
    [(2, 10), (3, 1), (4, 9), (5, 8), (6, 7)],
    [(10, 7), (8, 6), (9, 5), (1, 4), (2, 3)],
    [(3, 10), (4, 2), (5, 1), (6, 9), (7, 8)],
    [(10, 8), (9, 7), (1, 6), (2, 5), (3, 4)],
    [(4, 10), (5, 3), (6, 2), (7, 1), (8, 9)],
    [(10, 9), (1, 8), (2, 7), (3, 6), (4, 5)],
    [(5, 10), (6, 4), (7, 3), (8, 2), (9, 1)],
]


def test_matches_fide_table_for_ten_players_with_colours():
    got = [[(p.white, p.black) for p in r.pairings] for r in generate_schedule(10).rounds]
    assert got == FIDE_TABLE_10


@pytest.mark.parametrize("n_players", list(range(2, 41)))
def test_pairings_follow_modular_sum_rule(n_players):
    schedule = generate_schedule(n_players)
    table = n_players + 1 if n_players % 2 else n_players
    m = table - 1
    assert len(schedule.rounds) == m
    for t, rnd in enumerate(schedule.rounds):
        expected = {
            frozenset((a, b))
            for a in range(1, m + 1)
            for b in range(a + 1, m + 1)
            if (a + b - (t + 2)) % m == 0
        }
        (opp,) = [a for a in range(1, m + 1) if (2 * a - (t + 2)) % m == 0]
        if n_players % 2:
            assert rnd.bye == opp
        else:
            assert rnd.bye is None
            expected.add(frozenset((opp, table)))
        assert {frozenset((p.white, p.black)) for p in rnd.pairings} == expected


@pytest.mark.parametrize("double_round", [False, True])
@pytest.mark.parametrize("n_players", list(range(2, 31)))
def test_games_and_colours_by_enumeration(n_players, double_round):
    schedule = generate_schedule(n_players, double_round)
    meetings: dict[frozenset, list[int]] = {}
    white = [0] * (n_players + 1)
    black = [0] * (n_players + 1)
    for rnd in schedule.rounds:
        for p in rnd.pairings:
            meetings.setdefault(frozenset((p.white, p.black)), []).append(p.white)
            white[p.white] += 1
            black[p.black] += 1
    per_pair = 2 if double_round else 1
    assert len(meetings) == n_players * (n_players - 1) // 2
    for whites in meetings.values():
        assert len(whites) == per_pair
        if double_round:
            assert whites[0] != whites[1]
    if n_players >= 3:
        assert all(abs(white[i] - black[i]) <= 1 for i in range(1, n_players + 1))
