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


def test_transpose_with_riff_major(client, riff_major):
    payload = {"riff_id": riff_major.id,
               "pitch": "d",
               "chord_info": "C",  # Will be overruled with: `c1:maj9`
               }
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1"


def test_transpose_without_chord_info(client, riff):
    payload = {"riff_id": riff.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7",
               "chord_info_backing_track": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj9"
    # Should be passed trough as is:
    assert response.json["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json["chord_info_backing_track"] == "d1:m7 d1:9 fis1:maj7"


def test_transpose_without_riff_chord_info(client, riff_without_chord_info):
    payload = {"riff_id": riff_without_chord_info.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7",
               "chord_info_backing_track": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj"
    # Should be passed trough as is:
    assert response.json["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json["chord_info_backing_track"] == "d1:m7 d1:9 fis1:maj7"


def test_transpose_with_alternate_chord_info(client, exercise_1):
    # find an exercise_item_id in the exercise
    exercise_item = RiffExerciseItem.query.filter(RiffExerciseItem.order_number == 0).first()

    payload = {"exercise_item_id": exercise_item.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    # Should be passed trough as is:
    assert response.json["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"


def test_transpose_with_backing_track_chord_info(client, exercise_1):
    # find an exercise_item_id in the exercise
    exercise_item = RiffExerciseItem.query.filter(RiffExerciseItem.order_number == 0).first()

    payload = {"exercise_item_id": exercise_item.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7",
               "chord_info_backing_track": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    # Should be passed trough as is:
    assert response.json["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json["chord_info_backing_track"] == "d1:m7 d1:9 fis1:maj7"


def test_transpose_with_multiple_riffs(client, riff_without_chord_info):
    payload = [{"riff_id": riff_without_chord_info.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7",
               "chord_info_backing_track": "d1:m7 d1:9 fis1:maj7"},
               {"riff_id": riff_without_chord_info.id,
                "pitch": "e",
                "chord_info_alternate": "e1:m7 e1:9 gis1:maj7",
                "chord_info_backing_track": "e1:e7 e1:9 gis1:maj7"}]
    response = client.post('/v1/exercises/transpose-riffs', json=payload, follow_redirects=True)

    assert response.json[0]["chord_info"] == "d1:maj"
    assert response.json[1]["chord_info"] == "e1:maj"

    # Todo: Investigate if this is what we want in multi mode
    # Should be passed trough as is:
    assert response.json[0]["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json[0]["chord_info_backing_track"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json[1]["chord_info_alternate"] == "e1:m7 e1:9 gis1:maj7"
    assert response.json[1]["chord_info_backing_track"] == "e1:e7 e1:9 gis1:maj7"


# Todo: Maybe needs to be transformed to relative
def test_transpose_with_multiple_riffs_and_exercise_info(client, exercise_1):
    # find an exercise_item_id in the exercise
    exercise_item1 = RiffExerciseItem.query.filter(RiffExerciseItem.order_number == 0).first()
    exercise_item2 = RiffExerciseItem.query.filter(RiffExerciseItem.order_number == 2).first()

    payload = [{"exercise_item_id": exercise_item1.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7",
               "chord_info_backing_track": "d1:m7 d1:9 fis1:maj7"},
               {"exercise_item_id": exercise_item1.id,
                "pitch": "g",
                "chord_info_alternate": "d1:m7 d1:9 fis1:maj7",
                "chord_info_backing_track": "d1:m7 d1:9 fis1:maj7"}
               ]
    response = client.post('/v1/exercises/transpose-riffs', json=payload, follow_redirects=True)

    # Todo: Investigate if this is what we want in multi mode (we might need relative pitch change here)
    # Should be passed trough as is:
    assert response.json[0]["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json[0]["chord_info_backing_track"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json[1]["chord_info_alternate"] == "d1:m7 d1:9 fis1:maj7"
    assert response.json[1]["chord_info_backing_track"] == "d1:m7 d1:9 fis1:maj7"