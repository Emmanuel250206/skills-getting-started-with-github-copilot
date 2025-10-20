from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

TEST_EMAIL = "test.student@mergington.edu"


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of the original data and restore after each test
    original = {k: {**v, "participants": list(v.get("participants", []))} for k, v in activities.items()}
    yield
    activities.clear()
    activities.update({k: {**v, "participants": list(v.get("participants", []))} for k, v in original.items()})


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup():
    r = client.post(f"/activities/Chess Club/signup?email={TEST_EMAIL}")
    assert r.status_code == 200
    assert TEST_EMAIL in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    # Signup the same email twice to trigger 400
    r1 = client.post(f"/activities/Chess Club/signup?email={TEST_EMAIL}")
    assert r1.status_code == 200
    r2 = client.post(f"/activities/Chess Club/signup?email={TEST_EMAIL}")
    assert r2.status_code == 400


def test_delete_participant():
    # Ensure participant exists
    email = activities["Chess Club"]["participants"][0]
    r = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert r.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_delete_missing():
    r = client.delete("/activities/Chess Club/participants?email=notfound@example.com")
    assert r.status_code == 404
