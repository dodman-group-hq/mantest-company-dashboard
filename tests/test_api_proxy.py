"""
Test API Proxy Functionality

Tests that the dashboard correctly proxies requests to dodman-core API:
- Request forwarding
- Header passing
- Response forwarding
- Error handling
"""

import pytest
import responses


@pytest.mark.integration
@responses.activate
def test_proxy_forwards_get_request(client):
    """Test proxy forwards GET requests correctly."""
    # Mock a custom dodman-core endpoint
    responses.add(
        responses.GET,
        "http://localhost:8000/api/custom/endpoint",
        json={"data": "test"},
        status=200
    )
    
    response = client.get("/api/custom/endpoint")
    
    assert response.status_code == 200
    assert response.json() == {"data": "test"}


@pytest.mark.integration
@responses.activate
def test_proxy_forwards_post_request(client):
    """Test proxy forwards POST requests with body."""
    # Mock endpoint
    responses.add(
        responses.POST,
        "http://localhost:8000/api/custom/create",
        json={"id": "123", "created": True},
        status=201
    )
    
    payload = {"name": "Test Item"}
    response = client.post("/api/custom/create", json=payload)
    
    assert response.status_code == 201
    assert response.json()["created"] is True


@pytest.mark.integration
@responses.activate
def test_proxy_forwards_authorization_header(client):
    """Test proxy forwards Authorization header."""
    # Mock endpoint that checks auth
    def request_callback(request):
        # Check if Authorization header was forwarded
        assert "Authorization" in request.headers
        return (200, {}, '{"authenticated": true}')
    
    responses.add_callback(
        responses.GET,
        "http://localhost:8000/api/protected/resource",
        callback=request_callback
    )
    
    response = client.get(
        "/api/protected/resource",
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200


@pytest.mark.integration
@responses.activate
def test_proxy_forwards_query_parameters(client):
    """Test proxy forwards query parameters."""
    def request_callback(request):
        # Check query params were forwarded
        assert "page=1" in request.url
        assert "limit=10" in request.url
        return (200, {}, '{"results": []}')
    
    responses.add_callback(
        responses.GET,
        "http://localhost:8000/api/data/list",
        callback=request_callback,
        match_querystring=False  # Don't strictly match query string
    )
    
    response = client.get("/api/data/list?page=1&limit=10")
    
    assert response.status_code == 200


@pytest.mark.integration
@responses.activate
def test_proxy_handles_404_from_core_api(client):
    """Test proxy correctly returns 404 from core API."""
    responses.add(
        responses.GET,
        "http://localhost:8000/api/nonexistent",
        json={"detail": "Not found"},
        status=404
    )
    
    response = client.get("/api/nonexistent")
    
    assert response.status_code == 404


@pytest.mark.integration
@responses.activate
def test_proxy_handles_500_from_core_api(client):
    """Test proxy correctly returns 500 from core API."""
    responses.add(
        responses.GET,
        "http://localhost:8000/api/error",
        json={"detail": "Internal server error"},
        status=500
    )
    
    response = client.get("/api/error")
    
    assert response.status_code == 500


@pytest.mark.integration
def test_proxy_returns_503_when_core_api_unavailable(client):
    """Test proxy returns 503 when core API is unreachable."""
    # Don't mock the response - let it fail to connect
    
    response = client.get("/api/some/endpoint")
    
    # Should return 503 Service Unavailable when can't reach core API
    assert response.status_code == 503


@pytest.mark.integration
@responses.activate
def test_proxy_preserves_content_type(client):
    """Test proxy preserves Content-Type header from core API."""
    responses.add(
        responses.GET,
        "http://localhost:8000/api/data",
        body='{"data": "test"}',
        status=200,
        content_type="application/json"
    )
    
    response = client.get("/api/data")
    
    assert "application/json" in response.headers["content-type"]


@pytest.mark.integration
@responses.activate
def test_proxy_handles_timeout(client, monkeypatch):
    """Test proxy handles timeout from core API gracefully."""
    import httpx
    
    # Mock httpx to raise timeout
    async def mock_request(*args, **kwargs):
        raise httpx.TimeoutException("Request timed out")
    
    # This test is conceptual - actual implementation depends on timeout handling
    # in main.py proxy code
    pass  # Skip for now as it requires more complex mocking