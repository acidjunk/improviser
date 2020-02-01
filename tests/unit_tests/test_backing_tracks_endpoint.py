import uuid
from unittest import mock

from tests.unit_tests.conftest import QUICK_TOKEN

def test_backing_track_for_exercise(client, student_logged_in, exercise_1):
    headers = {"Quick-Authentication-Token": f"{student_logged_in.id}:{QUICK_TOKEN}"}
    headers["Content-Type"] = "application/json"

    # somehow check_quick_token() loses the request in test setup
    with mock.patch('security.check_quick_token', return_value=True):
        with mock.patch('flask_principal.Permission.can', return_value=True):
            response = client.get(f'/v1/backing-tracks/for/{exercise_1.id}', headers=headers, follow_redirects=True)
            assert response.status_code == 200
            response = client.get(f'/v1/backing-tracks/for/NONEXISTINGID', headers=headers, follow_redirects=True)
            assert response.status_code == 400
            response = client.get(f'/v1/backing-tracks/for/111', headers=headers, follow_redirects=True)
            assert response.status_code == 400
            response = client.get(f'/v1/backing-tracks/for/{str(uuid.uuid4())}', headers=headers, follow_redirects=True)
            assert response.status_code == 404
            assert "not found" in response.json["message"]
