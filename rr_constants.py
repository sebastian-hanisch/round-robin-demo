"""Regler-Grenzen, Presets und Konstanten für die Rundenturnier-Demo.

Die Zirkelmethode ist ein reiner Konstruktionsalgorithmus (kein Zufall im
Spiel) - anders als sonst im Portfolio gibt es deshalb weder einen
Zufalls-Seed noch einen "Neu würfeln"-Regler.
"""

# --- Regler --------------------------------------------------------------
DEFAULT_N_PLAYERS = 8
N_PLAYERS_MIN, N_PLAYERS_MAX = 4, 20
DEFAULT_DOUBLE_ROUND = False

GROWTH_CHART_MAX_N = 100

# --- Presets ---------------------------------------------------------------
_BASE = {"n_players": DEFAULT_N_PLAYERS, "double_round": False}
PRESETS = {
    "Kleiner Vereinsabend (6 Spieler)": {**_BASE, "n_players": 6},
    "Ungerade Teilnehmerzahl (7 Spieler, mit Freilos)": {**_BASE, "n_players": 7},
    "Doppelrunde hin und zurück (8 Spieler)": {**_BASE, "n_players": 8, "double_round": True},
    "Warum nicht bei größeren Turnieren? (20 Spieler)": {**_BASE, "n_players": 20},
}
PRESET_HELP = {
    "Kleiner Vereinsabend (6 Spieler)": "6 Spieler, 5 Runden, jeder gegen jeden - der klassische Fall, für den ein Rundenturnier gemacht ist.",
    "Ungerade Teilnehmerzahl (7 Spieler, mit Freilos)": "Bei ungerader Teilnehmerzahl bekommt in jeder Runde ein Spieler ein Freilos (spielfrei) - die Demo nutzt intern dieselbe Tafel wie für 8 Spieler.",
    "Doppelrunde hin und zurück (8 Spieler)": "Jedes Paar spielt zweimal, mit getauschten Farben - 14 statt 7 Runden. Die letzten beiden Runden der Hinrunde werden vertauscht, damit niemand dreimal in Folge dieselbe Farbe bekommt.",
    "Warum nicht bei größeren Turnieren? (20 Spieler)": "Schon bei 20 Spielern sind es 19 Runden - für ein Wochenendturnier praktisch nicht mehr machbar. Das Rundenzahl-Wachstum-Diagramm unten zeigt, wie schnell das weiter wächst.",
}
