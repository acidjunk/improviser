import pytest
from apis.v1.exercises import transpose_chord_info


def test_transpose_chord_info_lilypond_progression():
    chord_info = "d2:m7 g:7 c1:maj7"
    mapping = {
        "d": "e2:m7 a:7 d1:maj7",
        "e": "fis2:m7 b:7 e1:maj7",
        "f": "g2:m7 c:7 f1:maj7",
        "g": "a2:m7 d:7 g1:maj7",
        "a": "b2:m7 e:7 a1:maj7",
        "b": "cis2:m7 fis:7 b1:maj7",
    }
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch) == lilypond


def test_transpose_chord_info_lilypond_var_1():
    chord_info = "c1:m7 c1:9 c1:maj7"
    mapping = {
        "c": "c1:m7 c1:9 c1:maj7",
        "cis": "cis1:m7 cis1:9 cis1:maj7",
        "ees": "ees1:m7 ees1:9 ees1:maj7",
        "gis": "gis1:m7 gis1:9 gis1:maj7",
    }
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch) == lilypond


def test_transpose_chord_info_dominant7():
    chord_info = "C7"
    mapping = {
        "cis": "cis1:7 cis1:7",
        "d": "d1:7 d1:7",
        "ees": "ees1:7 ees1:7",
        "e": "e1:7 e1:7",
    }
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch, number_of_bars=2) == lilypond
    mapping = {
        "cis": "cis1:7",
        "d": "d1:7",
        "ees": "ees1:7",
        "e": "e1:7",
    }
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch, number_of_bars=1) == lilypond


def test_transpose_chord_info_major():
    chord_info = "CM"
    pitch = "d"
    mapping = {"cis": "cis1:maj", "d": "d1:maj", "ees": "ees1:maj", "e": "e1:maj"}
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch) == lilypond


def test_transpose_chord_info_major7():
    chord_info = "CM7"
    pitch = "d"
    mapping = {"cis": "cis1:maj7", "d": "d1:maj7", "ees": "ees1:maj7", "e": "e1:maj7"}
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch) == lilypond


def test_transpose_chord_info_minor7():
    chord_info = "Cm7"
    mapping = {"cis": "cis1:m7", "d": "d1:m7", "ees": "ees1:m7", "e": "e1:m7"}
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch) == lilypond


def test_transpose_chord_info_minor():
    chord_info = "Cm"
    mapping = {"cis": "cis1:m", "d": "d1:m", "ees": "ees1:m", "e": "e1:m"}
    for pitch, lilypond in mapping.items():
        assert transpose_chord_info(chord_info, pitch) == lilypond


def test_wrong_chord():
    chord_info = "Cm19aug12b3"
    with pytest.raises(Exception):
        transpose_chord_info(chord_info, "d")
