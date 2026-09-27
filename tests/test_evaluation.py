from __future__ import annotations

import pytest

from rr_evaluation import (
    colour_balance,
    games_played,
    max_colour_difference,
    round_growth_table,
)
from rr_scheduler import generate_schedule


def test_colour_balance_sums_to_round_count_per_player():
    schedule = generate_schedule(8)
    for cb in colour_balance(schedule):
        assert cb.white_games + cb.black_games == len(schedule.rounds)


def test_colour_balance_matches_known_fide_table_player_one():
    # Aus der echten FIDE-8er-Tafel von Hand nachgerechnet (s. test_scheduler.py):
    # Spieler 1 -> W,W,B,W,B,W,B = 4 Weiß, 3 Schwarz.
    schedule = generate_schedule(8)
    cb = next(c for c in colour_balance(schedule) if c.player == 1)
    assert (cb.white_games, cb.black_games) == (4, 3)


@pytest.mark.parametrize("n_players", list(range(4, 31)))
def test_max_colour_difference_at_most_one(n_players):
    schedule = generate_schedule(n_players)
    assert max_colour_difference(schedule) <= 1


def test_round_growth_table_matches_formula():
    table = round_growth_table(n_max=20)
    lookup = dict(table)
    assert lookup[4] == 3
    assert lookup[8] == 7
    assert lookup[20] == 19


def test_round_growth_table_double_round_doubles_counts():
    single = dict(round_growth_table(n_max=20, double_round=False))
    double = dict(round_growth_table(n_max=20, double_round=True))
    for n in single:
        assert double[n] == single[n] * 2


def test_games_played_matches_total_pairs():
    schedule = generate_schedule(8)
    assert games_played(schedule) == 8 * 7 // 2
