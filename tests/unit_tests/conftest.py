import pytest

@pytest.fixture()
def riffs_json():
    json = """[
        {
            "name": "Test riff uno",
            "number_of_bars": 2,
            "notes": "c b e d d d e e",
            "chord": "Cm7"
        },
        {
            "name": "Test riff fod",
            "number_of_bars": 2,
            "notes": "f f b b e e g g",
            "chord": "Fm9"
        }
    ]"""
    return json
