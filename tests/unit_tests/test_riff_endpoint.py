
def test_riffs_endpoint_without_riffs(client):
    response = client.get('/v1/riffs', json={}, follow_redirects=True)


def test_riffs_endpoint(client, riff):
    return client.get('/v1/riffs', json={}, follow_redirects=True)
