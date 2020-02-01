
def test_normalised_chord_info(app, exercise_1):
    chord_info = exercise_1.get_normalised_chord_info
    assert chord_info == "floempje"
