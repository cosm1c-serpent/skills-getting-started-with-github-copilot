import pytest
from fastapi.testclient import TestClient


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity(client: TestClient):
    """Test signing up for an activity"""
    # First get activities to find one to sign up for
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "test@example.com"

    # Sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client: TestClient):
    """Test signing up for the same activity twice"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "duplicate@example.com"

    # Sign up first time
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client: TestClient):
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_unregister_from_activity(client: TestClient):
    """Test unregistering from an activity"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "unregister@example.com"

    # Sign up first
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up(client: TestClient):
    """Test unregistering when not signed up"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "notsignedup@example.com"

    # Try to unregister without being signed up
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client: TestClient):
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]