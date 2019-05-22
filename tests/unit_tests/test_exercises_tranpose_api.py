from database import RiffExerciseItem, RiffExercise


def test_transpose_without_riff(client):
    payload = {"pitch": "d",
               "chord_info": "c1:m7 c1:9 c1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:m7 d1:9 d1:maj7"


def test_transpose_with_riff(client, riff):
    payload = {"riff_id": riff.id,
               "pitch": "d",
               "chord_info": "c1:m7 c1:9 c1:maj7",  # Will be overruled with: `c1:maj9`
               }
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj9"


def test_transpose_without_chord_info(client, riff):
    payload = {"riff_id": riff.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj9"


def test_transpose_without_riff_chord_info(client, riff_without_chord_info):
    payload = {"riff_id": riff_without_chord_info.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj"


def test_transpose_with_alternate_chord_info(client, exercise_1):
    # find an exercise_item_id in the exercise
    exercise_item = RiffExerciseItem.query.filter(RiffExerciseItem.order_number == 0).first()

    payload = {"exercise_item_id": exercise_item.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    # Should be passed trough as is:
    assert response.json["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
