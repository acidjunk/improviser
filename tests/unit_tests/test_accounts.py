from tests.unit_tests.conftest import STUDENT_EMAIL, STUDENT_PASSWORD, TEACHER_EMAIL, TEACHER_PASSWORD


def login(client, email, password):
    return client.post('/login', json=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', json={}, follow_redirects=True)


def test_student_login(client, student):
    """Make sure login and logout works."""
    view = login(client, STUDENT_EMAIL, STUDENT_PASSWORD)
    assert view.json["response"]["user"]["authentication_token"]
    assert view.status_code == 200

    view = login(client, STUDENT_EMAIL, "Wrong password")
    assert view.status_code == 500


def test_unconfirmed_student_login(client, student_unconfirmed):
    """Make sure login shows confirmation error."""
    view = login(client, STUDENT_EMAIL, STUDENT_PASSWORD)
    assert view.json["response"]["errors"]["email"][0] == "Email requires confirmation."
    assert view.status_code == 400


def test_teacher_login(client, teacher):
    """Make sure login and logout works."""
    view = login(client, TEACHER_EMAIL, TEACHER_PASSWORD)
    assert view.json["response"]["user"]["authentication_token"]
    assert view.status_code == 200

    view = login(client, STUDENT_EMAIL, "Wrong password")
    assert view.status_code == 500


def test_unconfirmed_teacher_login(client, teacher_unconfirmed):
    """Make sure login shows confirmation error."""
    view = login(client, TEACHER_EMAIL, TEACHER_PASSWORD)
    assert view.json["response"]["errors"]["email"][0] == "Email requires confirmation."
    assert view.status_code == 400
