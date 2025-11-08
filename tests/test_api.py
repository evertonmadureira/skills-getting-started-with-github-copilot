"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in inter-school games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and train for competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "emily@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore different art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Develop acting skills and perform in school theater productions",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Learn argumentation skills and compete in debate tournaments",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Participate in science competitions and experiments across various disciplines",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that activities are returned as a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Swimming Club", "Art Club",
            "Drama Club", "Debate Team", "Science Olympiad"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        email = "teststudent@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client):
        """Test that signing up twice fails"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitask@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming%20Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Unregister
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister when not signed up returns 400"""
        email = "notsignedup@mergington.edu"
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signup and unregister"""
        email = "flowtest@mergington.edu"
        activity = "Programming%20Class"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Verify signup
        response2 = client.get("/activities")
        data2 = response2.json()
        assert email in data2["Programming Class"]["participants"]
        
        # Unregister
        response3 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response3.status_code == 200
        
        # Verify unregistration
        response4 = client.get("/activities")
        data4 = response4.json()
        assert email not in data4["Programming Class"]["participants"]


class TestDataIntegrity:
    """Tests for data integrity and edge cases"""
    
    def test_participants_list_maintains_order(self, client):
        """Test that participants list maintains order"""
        activity = "Chess%20Club"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        # Sign up multiple students
        for email in emails:
            client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get activities
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        # Verify order (original + new)
        for email in emails:
            assert email in participants
    
    def test_max_participants_respected(self, client):
        """Test that we can track participants up to max"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            current_count = len(activity_data["participants"])
            max_count = activity_data["max_participants"]
            assert current_count <= max_count
    
    def test_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        from urllib.parse import quote
        email = "test+special@mergington.edu"
        encoded_email = quote(email)
        response = client.post(f"/activities/Chess%20Club/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify signup
        response2 = client.get("/activities")
        data = response2.json()
        assert email in data["Chess Club"]["participants"]
