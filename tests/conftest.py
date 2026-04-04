"""
Pytest Configuration and Shared Fixtures
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.main import app


# ============================================================================
# APP FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """
    FastAPI test client.
    
    Usage:
        def test_health(client):
            response = client.get("/health")
            assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_core_api_url():
    """Mock dodman-core API URL for testing."""
    return "http://127.0.0.1:8000"


# ============================================================================
# MOCK API FIXTURES
# ============================================================================

@pytest.fixture
def mock_auth_response():
    """Mock successful auth response."""
    return {
        "success": True,
        "message": "Magic link sent successfully",
        "tenant_id": "test_tenant",
        "sent_to": "test@example.com"
    }


@pytest.fixture
def mock_verify_response():
    """Mock successful token verification response."""
    return {
        "success": True,
        "user": {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "admin",
            "tenant_id": "test_tenant"
        },
        "session_token": "mock_session_token_xyz",
        "refresh_token": "mock_refresh_token_xyz",
        "expires_at": "2026-01-18T12:00:00"
    }


@pytest.fixture
def mock_plugins_response():
    """Mock plugins list response."""
    return {
        "plugins": [
            {
                "id": "sniper",
                "name": "Sniper",
                "description": "AI-powered lead capture",
                "icon": "🎯",
                "category": "intelligence",
                "status": "active",
                "version": "1.0.0"
            },
            {
                "id": "mirror",
                "name": "Mirror",
                "description": "Trial dashboard generator",
                "icon": "🪞",
                "category": "sales",
                "status": "active",
                "version": "1.0.0"
            }
        ]
    }


@pytest.fixture
def mock_dashboard_overview():
    """Mock dashboard overview data."""
    return {
        "metrics": {
            "total_leads": 42,
            "active_plugins": 2,
            "api_usage": 1250,
            "credit_remaining": 750.50
        },
        "recent_activity": [
            {
                "id": "act-1",
                "type": "lead_captured",
                "message": "New lead: John Doe",
                "timestamp": "2026-01-11T10:30:00"
            }
        ],
        "alerts": []
    }


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_email():
    """Test email address."""
    return "test@example.com"


@pytest.fixture
def test_subdomain():
    """Test subdomain."""
    return "testcompany"


@pytest.fixture
def test_tenant_id():
    """Test tenant ID."""
    return "testcompany_tenant"


@pytest.fixture
def test_magic_token():
    """Test magic link token."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJ0ZXN0X3RlbmFudCJ9.test"


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up temporary files after each test."""
    yield
    # Cleanup code here if needed
    import os
    temp_cookie_file = "/tmp/test-cookies.txt"
    if os.path.exists(temp_cookie_file):
        os.remove(temp_cookie_file)


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may mock external APIs)"
    )
    config.addinivalue_line(
        "markers", "frontend: Frontend/UI tests"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slower running tests"
    )