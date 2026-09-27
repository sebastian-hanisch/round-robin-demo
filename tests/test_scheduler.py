"""Abgleich gegen echte FIDE-Berger-Tafeln und Eigenschaftstests der Zirkelmethode.

Referenzdaten wörtlich aus handbook.fide.com/chapter/C05Annex1 (Stand
2026-09-27) übernommen - siehe project_turnierplanung_dag_scoping.md.
"""

from __future__ import annotations

import pytest

from rr_scheduler import Pairing, generate_schedule, round_count

# FIDE-Tafel "5 oder 6 Spieler": bei n_players=5 spielt Nr. 6 den Dummy (Bye).
FIDE_TABLE_6 = [
    [(1, 6), (2, 5), (3, 4)],
    [(6, 4), (5, 3), (1, 2)],
    [(2, 6), (3, 1), (4, 5)],
    [(6, 5), (1, 4), (2, 3)],
    [(3, 6), (4, 2), (5, 1)],
]

# FIDE-Tafel "7 oder 8 Spieler": bei n_players=7 spielt Nr. 8 den Dummy (Bye).
FIDE_TABLE_8 = [
    [(1, 8), (2, 7), (3, 6), (4, 5)],
    [(8, 5), (6, 4), (7, 3), (1, 2)],
    [(2, 8), (3, 1), (4, 7), (5, 6)],
    [(8, 6), (7, 5), (1, 4), (2, 3)],
    [(3, 8), (4, 2), (5, 1), (6, 7)],
    [(8, 7), (1, 6), (2, 5), (3, 4)],
    [(4, 8), (5, 3), (6, 2), (7, 1)],
]


def _as_pair_tuples(rounds) -> list[list[tuple[int, int]]]:
    return [[(p.white, p.black) for p in rnd.pairings] for rnd in rounds]


@pytest.mark.parametrize(
    "n_players, expected",
    [(6, FIDE_TABLE_6), (8, FIDE_TABLE_8)],
)
def test_matches_real_fide_table_exactly(n_players, expected):
    schedule = generate_schedule(n_players)
    got = _as_pair_tuples(schedule.rounds)
    assert got == expected, (
        f"Abweichung von der echten FIDE-Tafel für n={n_players}: "
        f"erwartet {expected}, bekommen {got}"
    )


def test_odd_five_reuses_six_table_with_bye_for_player_six_opponent():
    # Bei 5 Spielern wird intern die 6er-Tafel genutzt; wer gegen den Dummy
    # (Nr. 6) gezogen wird, hat in dieser Runde spielfrei (Bye), alle
    # anderen Paarungen entsprechen exakt der 6er-Tafel ohne den Dummy.
    schedule = generate_schedule(5)
    assert len(schedule.rounds) == 5
    for round_index, rnd in enumerate(schedule.rounds):
        expected_pairs_with_dummy = FIDE_TABLE_6[round_index]
        expected_real_pairs = [
            (w, b) for (w, b) in expected_pairs_with_dummy if 6 not in (w, b)
        ]
        expected_bye = next(
            p for pair in expected_pairs_with_dummy for p in pair if 6 in pair and p != 6
        )
        got_pairs = [(p.white, p.black) for p in rnd.pairings]
        assert got_pairs == expected_real_pairs
        assert rnd.bye == expected_bye


def test_odd_seven_reuses_eight_table_with_bye_for_player_eight_opponent():
    schedule = generate_schedule(7)
    assert len(schedule.rounds) == 7
    for round_index, rnd in enumerate(schedule.rounds):
        expected_pairs_with_dummy = FIDE_TABLE_8[round_index]
        expected_real_pairs = [
            (w, b) for (w, b) in expected_pairs_with_dummy if 8 not in (w, b)
        ]
        expected_bye = next(
            p for pair in expected_pairs_with_dummy for p in pair if 8 in pair and p != 8
        )
        got_pairs = [(p.white, p.black) for p in rnd.pairings]
        assert got_pairs == expected_real_pairs
        assert rnd.bye == expected_bye


@pytest.mark.parametrize("n_players", list(range(3, 31)))
def test_every_pair_meets_exactly_once_single_round_robin(n_players):
    schedule = generate_schedule(n_players, double_round=False)
    seen_pairs: set[frozenset[int]] = set()
    for rnd in schedule.rounds:
        for p in rnd.pairings:
            key = frozenset((p.white, p.black))
            assert key not in seen_pairs, f"Paar {key} spielt zweimal (n={n_players})"
            seen_pairs.add(key)
    expected_total = n_players * (n_players - 1) // 2
    assert len(seen_pairs) == expected_total


@pytest.mark.parametrize("n_players", list(range(3, 31)))
def test_every_pair_meets_exactly_twice_with_swapped_colour_double_round_robin(n_players):
    schedule = generate_schedule(n_players, double_round=True)
    counts: dict[frozenset[int], list[tuple[int, int]]] = {}
    for rnd in schedule.rounds:
        for p in rnd.pairings:
            key = frozenset((p.white, p.black))
            counts.setdefault(key, []).append((p.white, p.black))
    expected_pairs = n_players * (n_players - 1) // 2
    assert len(counts) == expected_pairs
    for key, games in counts.items():
        assert len(games) == 2, f"Paar {key} spielt nicht genau zweimal (n={n_players})"
        (w1, b1), (w2, b2) = games
        assert {w1, b1} == {w2, b2}
        assert (w1, b1) != (w2, b2), f"Paar {key} hat beide Male dieselbe Farbe (n={n_players})"


@pytest.mark.parametrize("n_players", list(range(3, 31)))
def test_each_player_has_exactly_one_game_or_bye_per_round(n_players):
    schedule = generate_schedule(n_players)
    for rnd in schedule.rounds:
        involved = []
        for p in rnd.pairings:
            involved.append(p.white)
            involved.append(p.black)
        if rnd.bye is not None:
            involved.append(rnd.bye)
        assert sorted(involved) == list(range(1, n_players + 1))
        assert rnd.bye is not None if n_players % 2 == 1 else rnd.bye is None


@pytest.mark.parametrize("n_players", list(range(4, 31, 2)))
def test_round_count_matches_formula(n_players):
    schedule = generate_schedule(n_players)
    assert len(schedule.rounds) == n_players - 1 == round_count(n_players)


@pytest.mark.parametrize("n_players", list(range(3, 31, 2)))
def test_round_count_matches_formula_odd(n_players):
    schedule = generate_schedule(n_players)
    assert len(schedule.rounds) == n_players == round_count(n_players)


@pytest.mark.parametrize("n_players", list(range(4, 31)))
def test_colour_difference_at_most_one_per_player_single_round_robin(n_players):
    schedule = generate_schedule(n_players, double_round=False)
    diff = {p: 0 for p in range(1, n_players + 1)}
    for rnd in schedule.rounds:
        for p in rnd.pairings:
            diff[p.white] += 1
            diff[p.black] -= 1
    bad = {player: d for player, d in diff.items() if abs(d) > 1}
    assert not bad, f"Farbdifferenz > 1 bei n={n_players}: {bad}"


def test_double_round_robin_round_count():
    schedule = generate_schedule(8, double_round=True)
    assert len(schedule.rounds) == 14


@pytest.mark.parametrize("n_players", list(range(4, 31)))
def test_double_round_robin_never_three_consecutive_same_colour(n_players):
    # FIDE empfiehlt das Vertauschen der letzten beiden Hinrunden-Runden genau
    # dafür (C.05 Annex 1) - hier über n=4..30 tatsächlich nachgemessen,
    # nicht nur angenommen.
    schedule = generate_schedule(n_players, double_round=True)
    per_player: dict[int, list[str]] = {}
    for rnd in schedule.rounds:
        for p in rnd.pairings:
            per_player.setdefault(p.white, []).append("W")
            per_player.setdefault(p.black, []).append("B")
    for player, sequence in per_player.items():
        run = 1
        for i in range(1, len(sequence)):
            run = run + 1 if sequence[i] == sequence[i - 1] else 1
            assert run <= 2, (
                f"n={n_players}: Spieler {player} hat {run} gleiche Farben in Folge"
            )


def test_pairing_is_frozen_dataclass():
    p = Pairing(white=1, black=2)
    with pytest.raises(Exception):
        p.white = 3  # type: ignore[misc]


def test_generate_schedule_rejects_too_few_players():
    with pytest.raises(ValueError):
        generate_schedule(1)
