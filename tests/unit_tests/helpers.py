def login(client, email, password):
    return client.post('/login', json=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)
