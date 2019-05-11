

def test_transpose_without_riff(client, student):
    payload = {"pitch": "d",
               "chord_info": "c1:m7 c1:9 c1:maj7",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7" }
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:m7 d1:9 d1:maj7"
    assert response.json["chord_info_alternate"] == "e1:m7 e1:9 g:maj7"


def test_transpose_with_riff(client, student, riff):
    payload = {"riff_id": riff.id,
               "pitch": "d",
               "chord_info": "c1:m7 c1:9 c1:maj7",  # Will be overruled with: `c1:maj9`
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj9"
    assert response.json["chord_info_alternate"] == "e1:m7 e1:9 g:maj7"


def test_transpose_without_chord_info(client, student, riff):
    payload = {"riff_id": riff.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj9"
    assert response.json["chord_info_alternate"] == "e1:m7 e1:9 g:maj7"


def test_transpose_without_riff_chord_info(client, student, riff_without_chord_info):
    payload = {"riff_id": riff_without_chord_info.id,
               "pitch": "d",
               "chord_info_alternate": "d1:m7 d1:9 fis1:maj7"}
    response = client.post('/v1/exercises/transpose-riff', json=payload, follow_redirects=True)

    assert response.json["chord_info"] == "d1:maj"
    assert response.json["chord_info_alternate"] == "e1:m7 e1:9 g:maj7"
