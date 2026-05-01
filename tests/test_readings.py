"""Road condition reading endpoint tests."""

import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestReadings:
    """Test reading submission and retrieval endpoints."""

    def test_submit_reading(self, client, auth_headers):
        """Test submitting a road condition reading."""
        # Create a segment first
        segment_response = client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "Test Segment for Readings",
                "location": "Test Location",
                "length_km": 2.0,
                "latitude": 40.0,
                "longitude": -120.0,
                "highway_type": "Interstate"
            }
        )
        segment_id = segment_response.json()["id"]

        # Submit a reading
        response = client.post(
            "/api/readings/submit",
            headers=auth_headers,
            json={
                "segment_id": segment_id,
                "device_id": "device-001",
                "latitude": 40.0,
                "longitude": -120.0,
                "temperature": 25.5,
                "humidity": 65,
                "surface_condition": "good",
                "surface_type": "asphalt",
                "roughness_index": 2.3,
                "pothole_count": 2,
                "crack_extent": 5.2
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["segment_id"] == segment_id
        assert data["status"] == "processing"
        assert "id" in data

    def test_get_readings_for_segment(self, client, auth_headers):
        """Test retrieving readings for a specific segment."""
        # Create segment
        segment_response = client.post(
            "/api/roads/segments",
            headers=auth_headers,
            json={
                "name": "Segment for Query",
                "location": "Test Location",
                "length_km": 1.5,
                "latitude": 35.0,
                "longitude": -118.0,
                "highway_type": "State Route"
            }
        )
        segment_id = segment_response.json()["id"]

        # Submit multiple readings
        for i in range(3):
            client.post(
                "/api/readings/submit",
                headers=auth_headers,
                json={
                    "segment_id": segment_id,
                    "device_id": f"device-{i:03d}",
                    "latitude": 35.0 + i * 0.01,
                    "longitude": -118.0 + i * 0.01,
                    "temperature": 20.0 + i,
                    "humidity": 60 + i * 5,
                    "surface_condition": "good",
                    "surface_type": "asphalt",
                    "roughness_index": 2.0 + i * 0.5,
                    "pothole_count": i,
                    "crack_extent": 3.0 + i * 2
                }
            )

        # Get readings
        response = client.get(
            f"/api/readings/segments/{segment_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "data" in data
        assert len(data["data"]) >= 3

    def test_submit_reading_invalid_segment(self, client, auth_headers):
        """Test submitting reading for non-existent segment."""
        response = client.post(
            "/api/readings/submit",
            headers=auth_headers,
            json={
                "segment_id": "nonexistent-segment",
                "device_id": "device-001",
                "latitude": 40.0,
                "longitude": -120.0,
                "temperature": 25.5,
                "humidity": 65,
                "surface_condition": "good",
                "surface_type": "asphalt",
                "roughness_index": 2.3,
                "pothole_count": 2,
                "crack_extent": 5.2
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
