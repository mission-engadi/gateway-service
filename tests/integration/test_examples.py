"""Integration tests for example endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.example import ExampleModel
from app.services.example_service import ExampleService


@pytest.mark.integration
class TestExampleEndpoints:
    """Test example CRUD endpoints."""
    
    def test_list_examples_requires_auth(self, client: TestClient):
        """Test that listing examples requires authentication."""
        response = client.get("/api/v1/examples/")
        assert response.status_code == 401
    
    def test_list_examples_with_auth(self, client: TestClient, auth_headers: dict):
        """Test listing examples with authentication."""
        response = client.get("/api/v1/examples/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_example(self, client: TestClient, auth_headers: dict):
        """Test creating an example."""
        example_data = {
            "title": "Test Example",
            "description": "This is a test example",
            "status": "active",
        }
        
        response = client.post(
            "/api/v1/examples/",
            json=example_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == example_data["title"]
        assert data["description"] == example_data["description"]
        assert data["status"] == example_data["status"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_example(self, client: TestClient, auth_headers: dict):
        """Test getting a specific example."""
        # Create an example first
        create_response = client.post(
            "/api/v1/examples/",
            json={"title": "Test", "status": "active"},
            headers=auth_headers,
        )
        example_id = create_response.json()["id"]
        
        # Get the example
        response = client.get(
            f"/api/v1/examples/{example_id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == example_id
    
    def test_get_nonexistent_example(self, client: TestClient, auth_headers: dict):
        """Test getting a nonexistent example returns 404."""
        response = client.get(
            "/api/v1/examples/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    def test_update_example(self, client: TestClient, auth_headers: dict):
        """Test updating an example."""
        # Create an example
        create_response = client.post(
            "/api/v1/examples/",
            json={"title": "Original", "status": "active"},
            headers=auth_headers,
        )
        example_id = create_response.json()["id"]
        
        # Update the example
        update_data = {"title": "Updated Title"}
        response = client.put(
            f"/api/v1/examples/{example_id}",
            json=update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
    
    def test_delete_example(self, client: TestClient, auth_headers: dict):
        """Test deleting an example."""
        # Create an example
        create_response = client.post(
            "/api/v1/examples/",
            json={"title": "To Delete", "status": "active"},
            headers=auth_headers,
        )
        example_id = create_response.json()["id"]
        
        # Delete the example
        response = client.delete(
            f"/api/v1/examples/{example_id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/examples/{example_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
