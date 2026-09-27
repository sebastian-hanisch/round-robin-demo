"""Rauchtests der Streamlit-Oberfläche per AppTest: Standard, jedes Preset, Randgrößen, Runden-Slider."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import rr_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    if setup is not None:
        setup(at)
        at.run()
        assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Warum nicht" in h.value for h in at.subheader)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders(name):
    p = C.PRESETS[name]

    def setup(at):
        at.session_state["n_players_slider"] = p["n_players"]
        at.session_state["double_round_toggle"] = p["double_round"]

    _run(setup)


def test_extreme_settings_render():
    def small(at):
        at.session_state["n_players_slider"] = C.N_PLAYERS_MIN
        at.session_state["double_round_toggle"] = False

    _run(small)

    def large(at):
        at.session_state["n_players_slider"] = C.N_PLAYERS_MAX
        at.session_state["double_round_toggle"] = True

    _run(large)


def test_odd_player_count_renders():
    def setup(at):
        at.session_state["n_players_slider"] = 7
        at.session_state["double_round_toggle"] = False

    _run(setup)


def test_round_slider_state_resets_when_player_count_changes():
    at = _run()
    at.session_state["round_slider"] = 3
    at.run()
    assert at.session_state["round_slider"] == 3
    at.session_state["n_players_slider"] = 6
    at.run()
    assert not at.exception
    assert at.session_state["round_slider"] == 1
