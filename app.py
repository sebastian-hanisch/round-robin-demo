"""Rundenturnier / Round-Robin-Scheduling (Zirkelmethode, Berger-Tafeln) - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo
EIN Verfahren - die Zirkelmethode für Rundenturnier-Spielpläne - an einem wachsenden Beispiel. Wurzel der
neuen "Turnierplanung"-Linie der "Konzepte"-Reihe (siehe README für die geplanten Nachfolger Schweizer System
und K.-o.-System).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import rr_constants as C
from rr_evaluation import colour_balance, games_played, max_colour_difference, round_growth_table
from rr_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from rr_scheduler import generate_schedule
from rr_visualization import (
    build_colour_balance_chart,
    build_growth_chart,
    build_pairing_circle,
    build_schedule_table,
)

st.set_page_config(page_title="Rundenturnier – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _schedule(n_players, double_round):
    return generate_schedule(n_players, double_round=double_round)


@st.cache_data(show_spinner=False)
def _growth(double_round):
    return round_growth_table(C.GROWTH_CHART_MAX_N, double_round=double_round)


st.title("♟️ Rundenturnier: die Zirkelmethode (Berger-Tafeln)")
st.markdown(
    """
Bei einem **Rundenturnier** ("jeder gegen jeden") spielt jeder Teilnehmer gegen jeden anderen genau einmal
(oder zweimal, hin und zurück). Die **Zirkelmethode** konstruiert einen solchen Spielplan mechanisch - sie ist
der Algorithmus hinter den **Berger-Tafeln**, die die FIDE für Schachturniere vorschreibt. Diese Demo baut den
Spielplan exakt nach dieser Vorschrift, mit demselben Farbausgleich (Weiß/Schwarz) wie im echten Turnier.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren vergleichen, zeigt "
    "diese Demo - erstes Stück der neuen Turnierplanung-Linie der \"Konzepte\"-Reihe - **ein** Verfahren an "
    "einem wachsenden Beispiel: die Zirkelmethode ist einfach und beweisbar fair, aber sie braucht ein Spiel "
    "gegen JEDEN - das skaliert nicht. Wie man mit einer festen, kleinen Rundenzahl trotzdem auskommt, zeigt "
    "das nächste Stück (Schweizer System)."
)

with st.expander("So funktioniert die Zirkelmethode", expanded=True):
    st.markdown(
        """
1. **Ein Spieler ist fix** (die höchste Nummer der Tafel). Bei ungerader Teilnehmerzahl wird ein Dummy-Spieler
   ergänzt - wer in einer Runde gegen ihn gezogen wird, hat spielfrei (Freilos).
2. **Alle anderen Spieler rotieren** um eine feste Position pro Runde, mit einer Schrittweite, die garantiert,
   dass jedes Paar am Ende genau einmal aufeinandertrifft - insgesamt **n−1 Runden** für n Teilnehmer.
3. **Farbzuteilung**: in jeder Paarung hat eine festgelegte Seite Weiß; der fixe Spieler wechselt die Farbe
   jede Runde (sonst bliebe er immer auf derselben Seite). Am Ende ist die Weiß/Schwarz-Differenz jedes
   Spielers höchstens 1.
4. **Doppelrunde** (optional): dieselben Paarungen noch einmal mit getauschten Farben: die letzten beiden
   Runden der Hinrunde werden dafür vertauscht, damit niemand dreimal in Folge dieselbe Farbe bekommt.

Diese Demo baut den Spielplan **exakt** nach den offiziellen FIDE-Berger-Tafeln nach (`handbook.fide.com`) -
geprüft in `tests/test_scheduler.py` Runde für Runde gegen die dort veröffentlichten Beispieltafeln.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_players = st.slider(
        "Teilnehmerzahl", *bounds("n_players_slider"), key="n_players_slider",
        help="Bei ungerader Zahl hat in jeder Runde ein Spieler ein Freilos.",
    )
    double_round = st.checkbox(
        "Doppelrunde (hin und zurück)", key="double_round_toggle",
        help="Jedes Paar spielt zweimal, mit getauschten Farben - doppelt so viele Runden.",
    )

sync_query_params(n_players, double_round)

n_players = int(n_players)
schedule = _schedule(n_players, bool(double_round))
n_rounds = len(schedule.rounds)

st.markdown("---")
st.markdown("## 🎯 Rotation und Paarungen")
st.caption(
    f"{n_players} Teilnehmer, {n_rounds} Runden"
    + (" (Doppelrunde)" if double_round else "")
    + " - jede Kante ist ein Spiel, jede Runde ein perfektes Matching (1-Faktorisierung des vollständigen Graphen)."
)

round_key = (n_players, double_round)
if "round_slider" not in st.session_state or st.session_state.get("round_owner") != round_key:
    st.session_state["round_slider"] = 1
    st.session_state["round_owner"] = round_key

rcol1, rcol2 = st.columns([5, 1])
with rcol1:
    round_number = st.slider("Runde", 1, n_rounds, key="round_slider")
with rcol2:
    auto_play = st.button("▶️ Abspielen", width="stretch")

circle_slot = st.empty()


def _render_round(r):
    circle_slot.plotly_chart(build_pairing_circle(schedule, r - 1), width="stretch", key=f"circle_{r}")


if auto_play:
    import time

    for r in range(1, n_rounds + 1):
        _render_round(r)
        time.sleep(0.4)
    round_number = n_rounds
else:
    _render_round(round_number)

current_round = schedule.rounds[round_number - 1]
pairing_lines = [f"**{p.white}** (Weiß) – **{p.black}** (Schwarz)" for p in current_round.pairings]
if current_round.bye is not None:
    pairing_lines.append(f"Spieler **{current_round.bye}**: Freilos")
st.caption("Runde " + str(round_number) + ": " + " · ".join(pairing_lines))

st.markdown("---")
st.markdown("## 🎯 Vollständige Turniertafel")
st.plotly_chart(build_schedule_table(schedule), width="stretch", key="schedule_table")
st.caption("W = Weiß gegen die genannte Spielernummer, S = Schwarz gegen die genannte Spielernummer.")

st.markdown("**Farbausgleich je Spieler**")
st.plotly_chart(build_colour_balance_chart(schedule), width="stretch", key="colour_balance")
diff = max_colour_difference(schedule)
st.caption(
    f"Größte Weiß/Schwarz-Differenz über alle {n_players} Spieler: **{diff}** "
    f"({games_played(schedule)} Partien insgesamt) - live geprüft, nicht behauptet."
)

st.markdown("---")

st.subheader("📐 Warum nicht immer ein Rundenturnier?")
st.markdown(
    """
Ein Rundenturnier braucht **n−1 Runden** für n Teilnehmer (bzw. n Runden inklusive Freilos-Runden bei
ungerader Zahl) - bei 8 Spielern sind das 7 Runden, machbar an einem Wochenende. Bei größeren Turnieren wächst
die Rundenzahl **linear** mit der Teilnehmerzahl weiter, ganz gleich, wie fair die Regel ist:
"""
)
growth_rows = _growth(bool(double_round))
st.plotly_chart(build_growth_chart(growth_rows, n_players), width="stretch", key="growth_chart")
st.caption(
    "Zum Vergleich: ein Schweizer-System-Turnier braucht bei jeder Teilnehmerzahl nur etwa 7-11 Runden "
    "(typische FIDE-Turnierpraxis, kein Messwert dieser Demo) - wie das mit einer festen, kleinen Rundenzahl "
    "trotzdem funktioniert, zeigt das nächste Stück dieser Linie (Schweizer System, FIDE-Dutch-Regelwerk)."
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Modell.** Ein Rundenturnier mit $n$ Teilnehmern entspricht einer **1-Faktorisierung** des vollständigen
Graphen $K_n$: einer Zerlegung der Kantenmenge in $n-1$ (bei geradem $n$) perfekte Matchings (Faktoren), von
denen jedes eine Runde bildet. Jede Kante (= jedes Spielerpaar) kommt in genau einem Faktor vor.

**Zirkelmethode.** Ein Spieler ist fix, die restlichen $n-1$ (stets ungerade) tragen Labels
$0, \dots, n-2$. Der wirksame Rundenindex $R$ läuft mit Schrittweite $k = \lceil (n-1)/2 \rceil$ durch alle
Labels modulo $n-1$ (Schrittweite und Labelzahl sind teilerfremd, deshalb wird jedes Label genau einmal
getroffen). Je Runde spielt der fixe Spieler gegen Label $R$, und für $i = 1, \dots, (n-2)/2$ wird Label
$(R-i) \bmod (n-1)$ gegen Label $(R+i) \bmod (n-1)$ gepaart - macht $\lfloor n/2 \rfloor$ Paarungen je Runde.

**Ungerade Teilnehmerzahl.** Ein Dummy-Spieler wird ergänzt (Tafelgröße $n+1$); wer in einer Runde gegen ihn
gezogen wird, hat Freilos. Damit sind es $n$ statt $n-1$ Runden.

**Farbzuteilung.** Aus den echten FIDE-Berger-Tafeln abgeleitet (s. `tests/test_scheduler.py`): die
"$R+i$"-Seite jeder Paarung hat stets Weiß; der fixe Spieler wechselt die Farbe jede Runde. Live geprüft über
$n = 4 \dots 30$: die Weiß/Schwarz-Differenz jedes Spielers bleibt dabei höchstens 1.

**Doppelrunde.** Die Rückrunde übernimmt dieselben Paarungen mit vertauschten Farben; die letzten beiden
Runden der Hinrunde werden vertauscht (FIDE-Empfehlung), was - ebenfalls gemessen über $n=4\dots30$ -
tatsächlich verhindert, dass ein Spieler dreimal in Folge dieselbe Farbe bekommt.

Implementiert in `rr_scheduler.py` (Zirkelmethode, Farbregel, Doppelrunde) und `rr_evaluation.py`
(Rundenzahl-Wachstum, Farbausgleich).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html)."
)
