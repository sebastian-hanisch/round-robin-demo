"""Circle-Method-Kernalgorithmus für Rundenturnier-Spielpläne (Berger-Tafeln).

Reproduziert die von der FIDE veröffentlichten Berger-Tafeln
(handbook.fide.com/chapter/C05Annex1) Runde für Runde exakt - Herleitung und
Abgleich gegen die echten FIDE-Tabellen in tests/test_scheduler.py.

Konstruktion: der höchste Spieler der Tafel (bei ungerader Teilnehmerzahl ein
Dummy = Teilnehmerzahl + 1) ist fix. Die restlichen Spieler tragen Labels
0..m-1 (m = Tafelgröße - 1, stets ungerade). Der "wirksame" Rundenindex R
wandert mit Schrittweite (m+1)//2 durch alle Labels (Schrittweite und
Tafelgröße sind teilerfremd, deshalb wird jedes Label genau einmal
getroffen). Je Runde spielt der Fixspieler gegen Label R, und für
i=1..(m-1)//2 wird Label (R-i) gegen Label (R+i) gepaart. Farbregel (aus den
FIDE-Tabellen abgeleitet, s. Tests): die "R+i"-Seite hat stets Weiß; der
Fixspieler wechselt die Farbe jede Runde (gerade Rundenzahl (0-indiziert) =
Schwarz, ungerade = Weiß).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pairing:
    white: int
    black: int


@dataclass(frozen=True)
class Round:
    pairings: tuple[Pairing, ...]
    bye: int | None


@dataclass(frozen=True)
class Schedule:
    n_players: int
    double_round: bool
    rounds: tuple[Round, ...]


def _single_cycle_rounds(n_players: int) -> list[Round]:
    if n_players < 2:
        raise ValueError("n_players muss mindestens 2 sein")

    is_odd = n_players % 2 == 1
    table_size = n_players + 1 if is_odd else n_players
    m = table_size - 1
    step = (m + 1) // 2
    fixed = table_size

    rounds: list[Round] = []
    r_pos = 0
    for round_index in range(m):
        opp = r_pos + 1
        pairings: list[Pairing] = []
        bye: int | None = None

        if is_odd:
            bye = opp
        else:
            if round_index % 2 == 0:
                white, black = opp, fixed
            else:
                white, black = fixed, opp
            pairings.append(Pairing(white=white, black=black))

        for i in range(1, (m - 1) // 2 + 1):
            a = (r_pos - i) % m + 1
            b = (r_pos + i) % m + 1
            pairings.append(Pairing(white=b, black=a))

        rounds.append(Round(pairings=tuple(pairings), bye=bye))
        r_pos = (r_pos + step) % m

    return rounds


def generate_schedule(n_players: int, double_round: bool = False) -> Schedule:
    """Baut den vollständigen Rundenturnier-Spielplan für n_players Teilnehmer.

    Bei double_round=True wird die Rückrunde mit vertauschten Farben
    angehängt; die letzten beiden Runden der Hinrunde werden dabei in der
    Präsentationsreihenfolge vertauscht (FIDE-Empfehlung C.05 Annex 1, um
    drei aufeinanderfolgende Partien mit derselben Farbe am Übergang zu
    vermeiden).
    """
    cycle1 = _single_cycle_rounds(n_players)

    if not double_round:
        return Schedule(n_players=n_players, double_round=False, rounds=tuple(cycle1))

    presented_cycle1 = list(cycle1)
    if len(presented_cycle1) >= 2:
        presented_cycle1[-1], presented_cycle1[-2] = presented_cycle1[-2], presented_cycle1[-1]

    cycle2 = [
        Round(
            pairings=tuple(Pairing(white=p.black, black=p.white) for p in rnd.pairings),
            bye=rnd.bye,
        )
        for rnd in cycle1
    ]

    return Schedule(
        n_players=n_players,
        double_round=True,
        rounds=tuple(presented_cycle1) + tuple(cycle2),
    )


def round_count(n_players: int, double_round: bool = False) -> int:
    """Rundenzahl ohne einen vollen Spielplan zu bauen (für die Wachstums-Grafik)."""
    single = n_players if n_players % 2 == 1 else n_players - 1
    return single * 2 if double_round else single
