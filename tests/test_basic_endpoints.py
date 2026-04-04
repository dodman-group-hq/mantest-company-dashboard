"""
Test Basic Endpoints

Tests for core application endpoints:
- Health check
- Root endpoint
- Static file serving
"""

import pytest


@pytest.mark.unit
def test_health_endpoint(client):
    """Test health check endpoint returns correct status."""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "master-dashboard-template"
    assert data["version"] == "1.0.0"
    assert "core_api" in data


@pytest.mark.unit
def test_root_endpoint_returns_html(client):
    """Test root endpoint serves index.html."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.unit
def test_verify_page_exists(client):
    """Test verify page endpoint exists."""
    response = client.get("/verify")
    
    # Should return HTML or redirect
    assert response.status_code in [200, 307]


@pytest.mark.unit
def test_nonexistent_route_404(client):
    """Test that nonexistent routes return 404."""
    response = client.get("/this-does-not-exist")
    
    assert response.status_code == 404


@pytest.mark.unit
def test_api_docs_accessible(client):
    """Test that API documentation is accessible."""
    response = client.get("/api/docs")
    
    assert response.status_code == 200


@pytest.mark.unit
def test_health_check_includes_core_api_url(client):
    """Test health check includes core API URL."""
    response = client.get("/health")
    
    data = response.json()
    assert "core_api" in data
    assert data["core_api"].startswith("http")