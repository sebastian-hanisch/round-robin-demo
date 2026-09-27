"""Plotly-Visualisierungen der Rundenturnier-Demo: Paarungs-Kreisdiagramm je Runde,
Rundenplan-Tabelle, Farbausgleich-Balken und das Rundenzahl-Wachstum-Diagramm (Hook).
Alle Figuren laufen durch `lock_axes` (Touch-Scrolling-Konvention des Portfolios)."""

from __future__ import annotations

import math

import plotly.graph_objects as go

from rr_evaluation import SWISS_TYPICAL_ROUNDS_MAX, SWISS_TYPICAL_ROUNDS_MIN, colour_balance
from rr_scheduler import Round, Schedule

WHITE_EDGE = "#d68a2e"
BLACK_EDGE = "#14233B"
NODE_FILL = "#1f77b4"
BYE_FILL = "#8a8f98"
GREEN = "#2ca02c"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True, visible=False)
    fig.update_yaxes(fixedrange=True, visible=False)
    return fig


def _circle_positions(n_players: int) -> dict[int, tuple[float, float]]:
    positions = {}
    for i in range(n_players):
        angle = math.pi / 2 - 2 * math.pi * i / n_players
        positions[i + 1] = (math.cos(angle), math.sin(angle))
    return positions


def build_pairing_circle(schedule: Schedule, round_index: int) -> go.Figure:
    """Alle Spieler fest auf einem Kreis (1..n); die Paarungen der gewählten Runde als Kanten -
    macht die Turniertafel als eine Kante pro Spieler und Runde sichtbar (1-Faktorisierung von K_n)."""
    n = schedule.n_players
    pos = _circle_positions(n)
    rnd: Round = schedule.rounds[round_index]

    fig = go.Figure()

    xs = [pos[p][0] for p in range(1, n + 1)]
    ys = [pos[p][1] for p in range(1, n + 1)]
    labels = [str(p) for p in range(1, n + 1)]
    colors = [BYE_FILL if rnd.bye == p else NODE_FILL for p in range(1, n + 1)]

    for pairing in rnd.pairings:
        x0, y0 = pos[pairing.white]
        x1, y1 = pos[pairing.black]
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=WHITE_EDGE, width=3),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            text=labels,
            textposition="middle center",
            textfont=dict(color="white", size=12),
            marker=dict(size=30, color=colors, line=dict(width=2, color="white")),
            hovertext=[
                f"Spieler {p}" + (" (Freilos diese Runde)" if rnd.bye == p else "")
                for p in range(1, n + 1)
            ],
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig.update_xaxes(range=[-1.3, 1.3])
    fig.update_yaxes(range=[-1.3, 1.3], scaleanchor="x", scaleratio=1)
    fig.update_layout(
        template="plotly_white",
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return lock_axes(fig)


def build_schedule_table(schedule: Schedule) -> go.Figure:
    """Klassische Turniertafel: Zeile = Spieler, Spalte = Runde, Zelle = Gegner + Farbe."""
    n = schedule.n_players
    n_rounds = len(schedule.rounds)

    opponent_by = {p: [None] * n_rounds for p in range(1, n + 1)}
    for r_idx, rnd in enumerate(schedule.rounds):
        for pairing in rnd.pairings:
            opponent_by[pairing.white][r_idx] = f"{pairing.black}W"
            opponent_by[pairing.black][r_idx] = f"{pairing.white}S"
        if rnd.bye is not None:
            opponent_by[rnd.bye][r_idx] = "Freilos"

    header = ["Spieler"] + [f"R{r + 1}" for r in range(n_rounds)]
    columns = [[str(p) for p in range(1, n + 1)]]
    for r_idx in range(n_rounds):
        columns.append([opponent_by[p][r_idx] for p in range(1, n + 1)])

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=header, fill_color="#14233B", font=dict(color="white"), align="center"),
                cells=dict(values=columns, align="center", height=26),
            )
        ]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=min(120 + n * 28, 900))
    return fig


def build_colour_balance_chart(schedule: Schedule) -> go.Figure:
    balances = colour_balance(schedule)
    players = [cb.player for cb in balances]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=players, y=[cb.white_games for cb in balances], name="Weiß", marker_color=WHITE_EDGE)
    )
    fig.add_trace(
        go.Bar(x=players, y=[-cb.black_games for cb in balances], name="Schwarz", marker_color=BLACK_EDGE)
    )
    fig.update_layout(
        template="plotly_white",
        barmode="relative",
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.2),
    )
    fig.update_xaxes(title="Spieler", dtick=1, fixedrange=True)
    fig.update_yaxes(title="Weiß-Partien (oben) / Schwarz-Partien (unten)", fixedrange=True)
    return fig


def build_growth_chart(rows: list[tuple[int, int]], current_n: int) -> go.Figure:
    ns = [n for n, _ in rows]
    rounds = [r for _, r in rows]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=ns, y=rounds, mode="lines", line=dict(color="#1f77b4", width=3), name="Rundenturnier")
    )
    fig.add_hrect(
        y0=SWISS_TYPICAL_ROUNDS_MIN,
        y1=SWISS_TYPICAL_ROUNDS_MAX,
        fillcolor=GREEN,
        opacity=0.15,
        line_width=0,
        annotation_text="Schweizer System, typische Rundenzahl",
        annotation_position="top left",
    )
    current_rounds = dict(rows).get(current_n)
    if current_rounds is not None:
        fig.add_trace(
            go.Scatter(
                x=[current_n],
                y=[current_rounds],
                mode="markers",
                marker=dict(size=14, color="#d68a2e", line=dict(width=1.5, color="#14233B")),
                name="aktuelle Auswahl",
            )
        )
    fig.update_xaxes(title="Teilnehmerzahl", fixedrange=True)
    fig.update_yaxes(title="Benötigte Rundenzahl", fixedrange=True, rangemode="tozero")
    fig.update_layout(
        template="plotly_white",
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig
