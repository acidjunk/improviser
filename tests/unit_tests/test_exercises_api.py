from unittest import mock

from tests.unit_tests.conftest import QUICK_TOKEN


def test_exercises_endpoint_without_auth(client):
    response = client.get('/v1/exercises', follow_redirects=True)
    assert response.status_code == 403


def test_riffs_detail_endpoint_without_auth(client, exercise_1):
    response = client.get(f'/v1/exercises/{exercise_1.id}', follow_redirects=True)
    assert response.status_code == 403


def test_exercises_endpoint_with_auth(client, teacher_logged_in, exercise_1, exercise_2):
    headers = {"Quick-Authentication-Token": f"{teacher_logged_in.id}:{QUICK_TOKEN}"}
    headers["Content-Type"] = "application/json"

    # somehow check_quick_token() loses the request in test setup
    with mock.patch('security.check_quick_token', return_value=True):
        with mock.patch('flask_principal.Permission.can', return_value=True):
            user = mock.MagicMock()
            user.id = teacher_logged_in.id
            with mock.patch('flask_login.utils._get_user', return_value=user):
                response = client.get('/v1/exercises', headers=headers, follow_redirects=True)
                assert response.status_code == 200
                assert len(response.json) == 2


def test_exercise_detail_endpoint_with_auth(client, teacher_logged_in, exercise_1):
    headers = {"Quick-Authentication-Token": f"{teacher_logged_in.id}:{QUICK_TOKEN}"}
    headers["Content-Type"] = "application/json"

    # somehow check_quick_token() loses the request in test setup
    with mock.patch('security.check_quick_token', return_value=True):
        with mock.patch('flask_principal.Permission.can', return_value=True):
            response = client.get(f'/v1/exercises/{exercise_1.id}', headers=headers, follow_redirects=True)
            assert response.status_code == 200
            response = client.get('/v1/exercises/1', headers=headers, follow_redirects=True)
            assert response.status_code == 404
            assert "exercise not found" in response.json["message"]
