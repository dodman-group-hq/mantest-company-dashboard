"""
Test Authentication Routes

Tests for authentication endpoints:
- Login (magic link request)
- Token verification
- Session management
- Logout
"""

import pytest
import responses


@pytest.mark.api
@responses.activate
def test_login_with_email(client, test_email, mock_auth_response):
    """Test login request with email."""
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        "http://localhost:8000/api/auth/request-magic-link",
        json=mock_auth_response,
        status=200
    )
    
    response = client.post(
        "/api/auth/login",
        json={"email": test_email}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert test_email in data.get("sent_to", "")


@pytest.mark.api
@responses.activate
def test_login_with_subdomain(client, test_subdomain, mock_auth_response):
    """Test login request with subdomain."""
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        "http://localhost:8000/api/auth/request-magic-link",
        json=mock_auth_response,
        status=200
    )
    
    response = client.post(
        "/api/auth/login",
        json={"subdomain": test_subdomain}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True


@pytest.mark.api
def test_login_without_email_or_subdomain(client):
    """Test login fails without email or subdomain."""
    response = client.post(
        "/api/auth/login",
        json={}
    )
    
    # Should return error (validation or 400)
    assert response.status_code in [400, 422]


@pytest.mark.api
@responses.activate
def test_verify_magic_link(client, test_magic_token, mock_verify_response):
    """Test magic link token verification."""
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        "http://localhost:8000/api/auth/verify-magic-link",
        json=mock_verify_response,
        status=200
    )
    
    response = client.post(
        "/api/auth/verify",
        json={"token": test_magic_token}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "user" in data
    
    # Check that cookies are set
    assert "session_token" in response.cookies or "Set-Cookie" in response.headers


@pytest.mark.api
@responses.activate
def test_verify_invalid_token(client):
    """Test verification fails with invalid token."""
    # Mock the dodman-core API error response
    responses.add(
        responses.POST,
        "http://localhost:8000/api/auth/verify-magic-link",
        json={"detail": "Invalid or expired magic link"},
        status=401
    )
    
    response = client.post(
        "/api/auth/verify",
        json={"token": "invalid_token"}
    )
    
    assert response.status_code == 401


@pytest.mark.api
@responses.activate
def test_logout(client):
    """Test logout endpoint."""
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        "http://localhost:8000/api/auth/logout",
        json={"success": True},
        status=200
    )
    
    # First, set a session cookie
    client.cookies.set("session_token", "test_token_123")
    
    response = client.post("/api/auth/logout")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    
    # Check that cookies are cleared
    # Cookie should be deleted or set to empty
    session_cookie = response.cookies.get("session_token")
    assert session_cookie == "" or session_cookie is None


@pytest.mark.api
@responses.activate
def test_refresh_session(client):
    """Test session refresh endpoint."""
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        "http://localhost:8000/api/auth/refresh-token",
        json={
            "success": True,
            "session_token": "new_session_token_xyz",
            "expires_at": "2026-01-18T12:00:00"
        },
        status=200
    )
    
    # Set a refresh token cookie
    client.cookies.set("refresh_token", "test_refresh_token")
    
    response = client.post("/api/auth/refresh")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True


@pytest.mark.api
def test_session_endpoint_without_cookie(client):
    """Test session endpoint returns unauthenticated without cookie."""
    response = client.get("/api/auth/session")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["authenticated"] is False