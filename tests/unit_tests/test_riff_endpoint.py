from unittest import mock

from tests.unit_tests.conftest import QUICK_TOKEN


def test_riffs_endpoint_without_auth(client):
    response = client.get('/v1/riffs', follow_redirects=True)
    assert response.status_code == 403


def test_riffs_detail_endpoint_without_auth(client, riff):
    response = client.get(f'/v1/riffs/{riff.id}', follow_redirects=True)
    assert response.status_code == 403


def test_riffs_endpoint_with_auth(client, student_logged_in, riff, riff_unrendered, riff_multi_chord):
    headers = {"Quick-Authentication-Token": f"{student_logged_in.id}:{QUICK_TOKEN}"}
    headers["Content-Type"] = "application/json"

    # somehow check_quick_token() loses the request in test setup
    with mock.patch('security.check_quick_token', return_value=True):
        with mock.patch('flask_principal.Permission.can', return_value=True):
            response = client.get('/v1/riffs', headers=headers, follow_redirects=True)
            assert response.status_code == 200
            assert len(response.json) == 2

            # test column search
            response = client.get('/v1/riffs/?range=[0,19]&sort=%5B%22created_at%22,%22DESC%22%5D&filter=%7B%27name%27:%27bebop%27%7D', headers=headers, follow_redirects=True)
            assert response.status_code == 200
            assert len(response.json) == 1

            # this actually doesn't need to be accesible with this user, but tests the query stuff easily
            response = client.get('/v1/riffs/unrendered', headers=headers, follow_redirects=True)
            assert response.status_code == 200
            assert len(response.json) == 1


def test_riff_detail_endpoint_with_auth(client, student_logged_in, riff):
    headers = {"Quick-Authentication-Token": f"{student_logged_in.id}:{QUICK_TOKEN}"}
    headers["Content-Type"] = "application/json"

    # somehow check_quick_token() loses the request in test setup
    with mock.patch('security.check_quick_token', return_value=True):
        with mock.patch('flask_principal.Permission.can', return_value=True):
            response = client.get(f'/v1/riffs/{riff.id}', headers=headers, follow_redirects=True)
            assert response.status_code == 200
            response = client.get('/v1/riffs/1', headers=headers, follow_redirects=True)
            assert response.status_code == 404
            assert "riff not found" in response.json["message"]
