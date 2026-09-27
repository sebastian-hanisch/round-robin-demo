# Rundenturnier – die Zirkelmethode (Berger-Tafeln) – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-round-robin-demo.streamlit.app/)**

Erstes Stück (Wurzel) der neuen **Turnierplanung-Linie** der "Konzepte"-Reihe für die Website "Sebastian Hanisch –
Operations Research und Machine Learning". Ein **Rundenturnier** ("jeder gegen jeden") lässt jeden Teilnehmer
gegen jeden anderen genau einmal antreten. Die **Zirkelmethode** konstruiert einen solchen Spielplan
mechanisch – sie ist der Algorithmus hinter den **Berger-Tafeln**, die die FIDE für Schachturniere vorschreibt.
Diese Demo baut den Spielplan **exakt** nach dieser Vorschrift, inklusive Farbausgleich (Weiß/Schwarz) und
Freilos-Regel bei ungerader Teilnehmerzahl.

Geplante Nachfolger dieser Linie:

```
Rundenturnier (Wurzel, dieses Stück)
 ├─ Schweizer System (FIDE-Dutch-Regelwerk, volle C1-C21-Kriterienhierarchie)   [geplant]
 └─ K.-o.-System + Setzliste (Bracket-Seeding)                                  [geplant]
```

## Ergebnis (Zahlen aus den Tests)

| Frage | Ergebnis |
|---|---|
| Stimmt der Spielplan mit den echten FIDE-Tafeln überein? | ✅ Für n = 6 und n = 8 Runde für Runde exakt identisch mit den in `handbook.fide.com/chapter/C05Annex1` veröffentlichten Beispieltafeln (Paarungen **und** Reihenfolge, nicht nur Mengengleichheit). |
| Trifft jedes Paar genau einmal aufeinander? | ✅ Für n = 3 … 30 geprüft (einfache Runde) bzw. genau zweimal mit getauschten Farben (Doppelrunde). |
| Bleibt der Farbausgleich fair? | ✅ Die Weiß/Schwarz-Differenz jedes Spielers liegt für n = 4 … 30 nie über 1. |
| Vermeidet die Doppelrunde drei gleiche Farben in Folge? | ✅ Für n = 4 … 30 gemessen: nach dem Vertauschen der letzten beiden Hinrunden-Runden (FIDE-Empfehlung) bekommt kein Spieler mehr als zwei gleiche Farben hintereinander. |
| Wie schnell wächst die nötige Rundenzahl? | ⚠️ Linear mit der Teilnehmerzahl: 7 Runden bei 8 Spielern, 19 bei 20, 99 bei 100 – ein Schweizer-System-Turnier braucht bei jeder Größe nur etwa 7–11 Runden (Turnierpraxis, kein Messwert dieser Demo). Genau diese Schwäche motiviert das nächste Stück der Linie. |

## Was die Demo zeigt

- **Rotation und Paarungen**: Kreisdiagramm mit allen Teilnehmern, die Paarungen der gewählten Runde als Kanten;
  Runden-Slider und ▶️ Abspielen animieren durch das ganze Turnier.
- **Vollständige Turniertafel**: klassische Zeile-Spieler/Spalte-Runde-Ansicht mit Gegner und Farbe je Zelle.
- **Farbausgleich je Spieler**: gestapeltes Balkendiagramm Weiß- gegen Schwarz-Partien.
- **Rundenzahl-Wachstum**: n = 4 … 100 gegen die benötigte Rundenzahl, mit Referenzband für die typische
  Schweizer-System-Rundenzahl – der Übergang zum nächsten Stück der Linie.
- **Presets**: kleiner Vereinsabend (6), ungerade Teilnehmerzahl mit Freilos (7), Doppelrunde (8), und ein
  Preset, das die Rundenzahl-Explosion bei 20 Teilnehmern zeigt.

## Was diese Demo nicht kann (und wohin das nächste Stück geht)

Ein Rundenturnier braucht ein Spiel gegen **jeden** Teilnehmer – das ist beweisbar fair, skaliert aber nicht:
bei 50 Spielern wären es 49 Runden, unrealistisch für ein Wochenendturnier. Das **Schweizer System**
(nächstes Stück, echtes FIDE-Dutch-Regelwerk) löst genau dieses Problem: eine feste, kleine Rundenzahl, dafür
werden die Paarungen jede Runde neu anhand der bisherigen Ergebnisse bestimmt statt vorab feststehend.

## Modell und Verfahren

- **Modell**: ein Rundenturnier mit n Teilnehmern entspricht einer **1-Faktorisierung** des vollständigen
  Graphen $K_n$ – einer Zerlegung der Kantenmenge in $n-1$ perfekte Matchings (eines je Runde).
- **Zirkelmethode** (`rr_scheduler.py`): der höchste Spieler der Tafel ist fix (bei ungerader Teilnehmerzahl ein
  Dummy = Teilnehmerzahl + 1, dessen Gegner in einer Runde Freilos hat). Die restlichen Spieler tragen Labels
  0…m-1 (m = Tafelgröße − 1). Ein wirksamer Rundenindex R läuft mit Schrittweite ⌈m/2⌉ durch alle Labels modulo
  m (teilerfremd, deshalb wird jedes Label genau einmal getroffen); je Runde spielt der fixe Spieler gegen
  Label R, und für i = 1…(m−1)/2 wird Label (R−i) gegen Label (R+i) gepaart.
- **Farbregel**: aus den echten FIDE-Tafeln abgeleitet – die "R+i"-Seite jeder Paarung hat stets Weiß, der fixe
  Spieler wechselt die Farbe jede Runde.
- **Doppelrunde**: die Rückrunde übernimmt dieselben Paarungen mit getauschten Farben; die letzten beiden
  Runden der Hinrunde werden dafür vertauscht (FIDE-Empfehlung, C.05 Annex 1).
- **Quellen**: [handbook.fide.com/chapter/C05Annex1](https://handbook.fide.com/chapter/C05Annex1) (Berger-Tafeln,
  Beispieldaten), [en.wikipedia.org/wiki/Round-robin_tournament](https://en.wikipedia.org/wiki/Round-robin_tournament)
  (Zirkelmethode, Farb-Grundregel).

## Verifikation

- **Gegen echte FIDE-Tafeln**: `tests/test_scheduler.py` vergleicht `generate_schedule(6)` und `generate_schedule(8)`
  Runde für Runde exakt gegen die veröffentlichten Beispieltafeln (inkl. der Freilos-Fälle n=5, n=7 über dieselben
  Tafeln).
- **Eigenschaftstests** über n = 3…30: jedes Paar genau einmal (einfach) bzw. zweimal mit getauschten Farben
  (Doppelrunde), genau ein Spiel oder Freilos je Spieler und Runde, Rundenzahlformel, Farbdifferenz ≤ 1, keine
  drei gleichen Farben in Folge bei Doppelrunde.
- **Streamlit-Rauchtests** (`tests/test_app.py`): Standardaufruf, jedes Preset, Randgrößen, ungerade
  Teilnehmerzahl, Zustands-Reset des Runden-Reglers bei geänderter Teilnehmerzahl.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-Oberfläche |
| `rr_constants.py` | Regler-Grenzen, Presets |
| `rr_presets.py` | Permalink- und Preset-Logik (Standardmuster des Portfolios) |
| `rr_scheduler.py` | Zirkelmethode: Rotation, Farbregel, Freilos, Doppelrunde |
| `rr_evaluation.py` | Rundenzahl-Wachstum, Farbausgleich-Kennzahlen |
| `rr_visualization.py` | Plotly: Paarungs-Kreisdiagramm, Turniertafel, Farbausgleich, Wachstums-Chart |
| `tests/` | FIDE-Referenztafel-Abgleich, Eigenschaftstests, Streamlit-Rauchtests |

## Lokal starten

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\streamlit run app.py
```

## Tests ausführen

```bash
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\python -m pytest tests -v
```

Die CI (`.github/workflows/tests.yml`) läuft auf Ubuntu mit Python 3.12, bei jedem Push und wöchentlich mit den
jeweils neuesten Bibliotheksversionen.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research
und Machine Learning. Interesse an einer maßgeschneiderten Lösung für Ihr Unternehmen?
[Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)
