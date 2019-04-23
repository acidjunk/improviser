import pytest


@pytest.mark.xfail(reason="Not implemented yet")
def test_riffs_endpoint(client):
    return client.get('/v1/riffs', json={}, follow_redirects=True)

