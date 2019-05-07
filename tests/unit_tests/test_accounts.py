from tests.unit_tests.conftest import STUDENT_EMAIL, STUDENT_PASSWORD, TEACHER_EMAIL, TEACHER_PASSWORD
from tests.unit_tests.helpers import login, logout


def test_student_login(client, student):
    """Make sure login and logout works."""
    response = login(client, STUDENT_EMAIL, STUDENT_PASSWORD)
    assert response.json["response"]["user"]["authentication_token"]
    assert response.status_code == 200
    logout(client)

    response = login(client, STUDENT_EMAIL, "Wrong password")
    assert response.status_code == 400
    assert response.json["response"]["errors"]["password"] == ['Invalid password']


def test_unconfirmed_student_login(client, student_unconfirmed):
    """Make sure login shows confirmation error."""
    response = login(client, STUDENT_EMAIL, STUDENT_PASSWORD)
    assert response.json["response"]["errors"]["email"][0] == "Email requires confirmation."
    assert response.status_code == 400


def test_teacher_login(client, teacher):
    """Make sure login and logout works."""
    response = login(client, TEACHER_EMAIL, TEACHER_PASSWORD)
    assert response.status_code == 200
    assert response.json["response"]["user"]["authentication_token"]
    logout(client)

    response = login(client, TEACHER_EMAIL, "Wrong password")
    assert response.status_code == 400
    assert response.json["response"]["errors"]["password"] == ['Invalid password']


def test_unconfirmed_teacher_login(client, teacher_unconfirmed):
    """Make sure login shows confirmation error."""
    response = login(client, TEACHER_EMAIL, TEACHER_PASSWORD)
    assert response.json["response"]["errors"]["email"][0] == "Email requires confirmation."
    assert response.status_code == 400


def test_quick_token_retrieval(app, client, student):
    response = login(client, STUDENT_EMAIL, STUDENT_PASSWORD)
    assert response.status_code == 200
    auth_token = response.json["response"]["user"]["authentication_token"]
    headers = {"Authentication-Token": auth_token}
    response = client.get('/v1/users/current-user', headers=headers)
    assert response.status_code == 200
    assert response.json["quick_token"]

