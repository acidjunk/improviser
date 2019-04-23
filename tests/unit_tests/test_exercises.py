import pytest
from apis.v1.exercises import transpose_chord_info


def test_transpose_chord_info_lilypond_progression():
    chord_info = "d2:m7 g:7 c1:maj7"
    pitch = "d"
    assert transpose_chord_info(chord_info, pitch) == "e2:m7 a:7 d1:maj7"


def test_transpose_chord_info_lilypond_var_1():
    chord_info = "c1:m7 c1:9 c1:maj7"
    pitch = "ees"
    assert transpose_chord_info(chord_info, pitch) == "ees1:m7 ees1:9 ees1:maj7"
    pitch = "cis"
    assert transpose_chord_info(chord_info, pitch) == "cis1:m7 cis1:9 cis1:maj7"


def test_transpose_chord_info_dominant7():
    chord_info = "C7"
    pitch = "d"
    number_of_bars = 2
    assert transpose_chord_info(chord_info, pitch, number_of_bars) == "d1:7 d1:7"


@pytest.mark.xfail(reason="N/A")
def test_transpose_chord_info_major7():
    chord_info = "CM7"
    pitch = "d"
    number_of_bars = 2
    assert transpose_chord_info(chord_info, pitch, number_of_bars) == "d1:maj7 d1:maj7"
