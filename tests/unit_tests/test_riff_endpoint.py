from unittest import mock

from tests.unit_tests.conftest import QUICK_TOKEN


def test_riffs_endpoint_without_auth(client):
    response = client.get('/v1/riffs', follow_redirects=True)
    assert response.status_code == 401


def test_riffs_endpoint_with_auth(client, student_logged_in, riff, riff_unrendered, riff_multi_chord):
    headers = {"Quick-Authentication-Token": f"{student_logged_in.id}:{QUICK_TOKEN}"}
    headers["Content-Type"] = "application/json"

    # somehow check_quick_token() loses the request in test setup
    with mock.patch('security.check_quick_token', return_value=True):
        with mock.patch('flask_principal.Permission.can', return_value=True):
            response = client.get('/v1/riffs', json={}, headers=headers, follow_redirects=True)
            assert response.status_code == 200
            assert len(response.json) == 2

            response = client.get('/v1/riffs?search_phrase=bebop', json={}, headers=headers, follow_redirects=True)
            assert response.status_code == 200
            assert len(response.json) == 1

            response = client.get('/v1/riffs/unrendered', json={}, headers=headers, follow_redirects=True)
            assert response.status_code == 200
            assert len(response.json) == 1
