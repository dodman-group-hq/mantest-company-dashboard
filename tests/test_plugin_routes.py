"""
Test Plugin Routes

Tests for plugin management endpoints:
- List plugins
- Get plugin details
- Execute plugin
- Plugin status
"""

import pytest
import responses


@pytest.mark.api
@responses.activate
def test_list_plugins(client, mock_plugins_response):
    """Test listing all available plugins."""
    # Mock the dodman-core API response
    responses.add(
        responses.GET,
        "http://localhost:8000/api/plugins",
        json=mock_plugins_response,
        status=200
    )
    
    response = client.get("/api/plugins")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "plugins" in data
    assert len(data["plugins"]) > 0
    
    # Check plugin structure
    first_plugin = data["plugins"][0]
    assert "id" in first_plugin
    assert "name" in first_plugin
    assert "status" in first_plugin


@pytest.mark.api
@responses.activate
def test_get_plugin_details(client):
    """Test getting specific plugin details."""
    plugin_id = "sniper"
    
    # Mock the dodman-core API response
    responses.add(
        responses.GET,
        f"http://localhost:8000/api/plugins/{plugin_id}",
        json={
            "plugin": {
                "id": plugin_id,
                "name": "Sniper",
                "description": "AI-powered lead capture",
                "status": "active",
                "version": "1.0.0"
            }
        },
        status=200
    )
    
    response = client.get(f"/api/plugins/{plugin_id}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "plugin" in data
    assert data["plugin"]["id"] == plugin_id


@pytest.mark.api
@responses.activate
def test_execute_plugin(client):
    """Test executing a plugin action."""
    plugin_id = "sniper"
    
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        f"http://localhost:8000/api/plugins/{plugin_id}/execute",
        json={
            "status": "success",
            "result": {
                "leads_found": 5,
                "sources_scanned": ["twitter"]
            }
        },
        status=200
    )
    
    payload = {
        "plugin_id": plugin_id,
        "action": "run_scour",
        "payload": {"source": "twitter"}
    }
    
    response = client.post(
        f"/api/plugins/{plugin_id}/execute",
        json=payload
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.api
@responses.activate
def test_get_plugin_status(client):
    """Test getting plugin status."""
    plugin_id = "sniper"
    
    # Mock the dodman-core API response
    responses.add(
        responses.GET,
        f"http://localhost:8000/api/plugins/{plugin_id}/status",
        json={
            "plugin_id": plugin_id,
            "status": "active",
            "last_run": "2026-01-11T10:00:00",
            "metrics": {
                "total_runs": 42,
                "success_rate": 98.5
            }
        },
        status=200
    )
    
    response = client.get(f"/api/plugins/{plugin_id}/status")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["plugin_id"] == plugin_id
    assert "status" in data


@pytest.mark.api
@responses.activate
def test_update_plugin_config(client):
    """Test updating plugin configuration."""
    plugin_id = "sniper"
    
    # Mock the dodman-core API response
    responses.add(
        responses.PUT,
        f"http://localhost:8000/api/plugins/{plugin_id}/config",
        json={
            "success": True,
            "config": {"max_leads_per_day": 200}
        },
        status=200
    )
    
    new_config = {"config": {"max_leads_per_day": 200}}
    
    response = client.put(
        f"/api/plugins/{plugin_id}/config",
        json=new_config
    )
    
    assert response.status_code == 200


@pytest.mark.api
@responses.activate
def test_pause_plugin(client):
    """Test pausing a plugin."""
    plugin_id = "sniper"
    
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        f"http://localhost:8000/api/plugins/{plugin_id}/pause",
        json={"status": "paused"},
        status=200
    )
    
    response = client.post(f"/api/plugins/{plugin_id}/pause")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "paused"


@pytest.mark.api
@responses.activate
def test_resume_plugin(client):
    """Test resuming a plugin."""
    plugin_id = "sniper"
    
    # Mock the dodman-core API response
    responses.add(
        responses.POST,
        f"http://localhost:8000/api/plugins/{plugin_id}/resume",
        json={"status": "active"},
        status=200
    )
    
    response = client.post(f"/api/plugins/{plugin_id}/resume")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "active"


@pytest.mark.api
def test_nonexistent_plugin_404(client):
    """Test accessing nonexistent plugin returns 404."""
    # Note: Depends on how dodman-core handles this
    # May need to mock 404 response
    
    plugin_id = "nonexistent_plugin"
    
    # This test may pass or fail depending on proxy behavior
    # Documenting expected behavior
    response = client.get(f"/api/plugins/{plugin_id}")
    
    # Should proxy to core API and return its response
    # Typically 404 or 503 if core API is unavailable
    assert response.status_code in [404, 503]