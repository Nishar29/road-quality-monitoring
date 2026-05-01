"""Road segment endpoint tests."""

import pytest
from fastapi import status


class TestRoadSegments:
    """Test road segment endpoints."""

    def test_create_segment(self, client, auth_headers):
        """Test creating a new road segment."""
        response = client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "Highway 101 - Section A",
                "location": "San Francisco, CA",
                "length_km": 5.2,
                "latitude": 37.7749,
                "longitude": -122.4194,
                "highway_type": "Interstate"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Highway 101 - Section A"
        assert data["length_km"] == 5.2
        assert "id" in data

    def test_get_segments(self, client, auth_headers):
        """Test retrieving all road segments."""
        # Create a segment first
        client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "Test Segment",
                "location": "Test Location",
                "length_km": 3.0,
                "latitude": 40.0,
                "longitude": -120.0,
                "highway_type": "State Route"
            }
        )

        response = client.get(
            "/api/roads/segments",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "data" in data
        assert len(data["data"]) > 0

    def test_get_segment_by_id(self, client, auth_headers):
        """Test retrieving a specific road segment."""
        # Create a segment
        create_response = client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "Specific Test Segment",
                "location": "Test Location",
                "length_km": 2.5,
                "latitude": 35.0,
                "longitude": -118.0,
                "highway_type": "County Road"
            }
        )
        segment_id = create_response.json()["id"]

        # Retrieve it
        response = client.get(
            f"/api/roads/segments/{segment_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == segment_id
        assert data["name"] == "Specific Test Segment"

    def test_update_segment(self, client, auth_headers):
        """Test updating a road segment."""
        # Create a segment
        create_response = client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "Original Name",
                "location": "Test Location",
                "length_km": 1.0,
                "latitude": 30.0,
                "longitude": -115.0,
                "highway_type": "Local Road"
            }
        )
        segment_id = create_response.json()["id"]

        # Update it
        response = client.put(
            f"/api/roads/segments/{segment_id}",
            headers=auth_headers,
            json={
                "name": "Updated Name",
                "location": "Updated Location",
                "length_km": 1.5,
                "latitude": 30.5,
                "longitude": -115.5,
                "highway_type": "Local Road"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["length_km"] == 1.5

    def test_delete_segment(self, client, auth_headers):
        """Test deleting a road segment."""
        # Create a segment
        create_response = client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "To Delete",
                "location": "Test Location",
                "length_km": 0.5,
                "latitude": 25.0,
                "longitude": -110.0,
                "highway_type": "Parking Lot"
            }
        )
        segment_id = create_response.json()["id"]

        # Delete it
        response = client.delete(
            f"/api/roads/segments/{segment_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        get_response = client.get(
            f"/api/roads/segments/{segment_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_segment(self, client, auth_headers):
        """Test retrieving a non-existent segment."""
        response = client.get(
            "/api/roads/segments/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthorized_access(self, client):
        """Test accessing endpoints without authentication."""
        response = client.get("/api/roads/segments")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
