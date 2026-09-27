"""Kennzahlen: Rundenzahl-Wachstum (die Überleitung zu Stück 2) und Farbausgleich.

Der Vergleichswert "Schweizer System braucht nur ~7-11 Runden" ist ein
Kontext-Fakt (FIDE-Turnierpraxis), kein Messwert dieses Stücks - er wird nur
als Referenzlinie im Wachstums-Chart gezeigt, nie als eigene Behauptung
dieser Demo verkauft.
"""

from __future__ import annotations

from dataclasses import dataclass

from rr_scheduler import Schedule, round_count

# Typischer Rundenzahl-Korridor für Schweizer-System-Turniere unabhängig von
# der Teilnehmerzahl (FIDE-Turnierpraxis, z. B. Vereinsmeisterschaften 7
# Runden, nationale Opens 9, größere internationale Opens bis 11).
SWISS_TYPICAL_ROUNDS_MIN = 7
SWISS_TYPICAL_ROUNDS_MAX = 11


@dataclass(frozen=True)
class ColourBalance:
    player: int
    white_games: int
    black_games: int

    @property
    def difference(self) -> int:
        return self.white_games - self.black_games


def colour_balance(schedule: Schedule) -> list[ColourBalance]:
    white = {p: 0 for p in range(1, schedule.n_players + 1)}
    black = {p: 0 for p in range(1, schedule.n_players + 1)}
    for rnd in schedule.rounds:
        for pairing in rnd.pairings:
            white[pairing.white] += 1
            black[pairing.black] += 1
    return [
        ColourBalance(player=p, white_games=white[p], black_games=black[p])
        for p in range(1, schedule.n_players + 1)
    ]


def max_colour_difference(schedule: Schedule) -> int:
    return max(abs(cb.difference) for cb in colour_balance(schedule))


def round_growth_table(n_max: int = 100, double_round: bool = False) -> list[tuple[int, int]]:
    """(Teilnehmerzahl, benötigte Rundenzahl) für n=4..n_max - die Hook-Kurve."""
    return [(n, round_count(n, double_round=double_round)) for n in range(4, n_max + 1)]


def games_played(schedule: Schedule) -> int:
    return sum(len(rnd.pairings) for rnd in schedule.rounds)
