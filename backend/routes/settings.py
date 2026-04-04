"""
Settings Routes for Master Dashboard Template

Handles all settings pages: ICP, Plugins, API
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import httpx
import logging
import secrets
import os

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/settings", tags=["Settings"])

# Get frontend directory path
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
SETTINGS_DIR = FRONTEND_DIR / "settings"

# Get dodman-core API URL from environment
DODMAN_CORE_API_URL = os.getenv("DODMAN_CORE_API_URL", "http://localhost:8080")

# ============================================================================
# HELPER FUNCTIONS - PROXY TO DODMAN-CORE
# ============================================================================

async def proxy_to_core(
    endpoint: str,
    method: str = "GET",
    data: dict = None,
    headers: dict = None
) -> dict:
    """
    Proxy request to dodman-core API.
    
    Args:
        endpoint: API endpoint (e.g., "/api/tenants/acme/plugins/sniper/status")
        method: HTTP method
        data: Request body
        headers: Additional headers (auth token from cookies)
    
    Returns:
        Response from dodman-core
    """
    url = f"{DODMAN_CORE_API_URL}{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=10.0)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers, timeout=10.0)
            elif method == "PUT":
                response = await client.put(url, json=data, headers=headers, timeout=10.0)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, timeout=10.0)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Return JSON response
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get('detail', 'Request failed')
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Failed to proxy to dodman-core: {e}")
        raise HTTPException(
            status_code=503,
            detail="dodman-core API unavailable"
        )


def get_auth_header(request: Request) -> dict:
    """Extract auth token from cookies and create Authorization header."""
    token = request.cookies.get('session_token')
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    return {"Authorization": f"Bearer {token}"}


def get_tenant_id(request: Request) -> str:
    """Extract tenant ID from request context or cookies."""
    # Try to get from cookies (set during login)
    tenant_id = request.cookies.get('tenant_id')
    
    if not tenant_id:
        # Fallback to path parameter if exists
        tenant_id = request.path_params.get('tenant_id')
    
    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Tenant ID not found"
        )
    
    return tenant_id

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ICPSettings(BaseModel):
    """ICP (Ideal Customer Profile) Settings"""
    industry: Optional[str] = None
    company_size: Optional[str] = None
    revenue_range: Optional[str] = None
    funding_stage: Optional[str] = None
    regions: List[str] = []
    countries: Optional[str] = None
    signals: List[str] = []
    include_keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None


class PluginToggleRequest(BaseModel):
    """Request to toggle plugin on/off"""
    enabled: bool

# ============================================================================
# SETTINGS PAGE ROUTES (HTMX)
# ============================================================================

@router.get("/icp")
async def icp_settings_page():
    """
    Serve ICP Settings page HTML.
    
    Route in index.html:
        <a href="/settings/icp" 
           hx-get="/api/settings/icp" 
           hx-target="#main-content">
    """
    settings_file = SETTINGS_DIR / "icp.html"
    
    if not settings_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"ICP settings page not found at {settings_file}"
        )
    
    return FileResponse(settings_file, media_type="text/html")


@router.get("/plugins")
async def plugins_settings_page():
    """
    Serve Plugin Manager page HTML.
    
    Route in index.html:
        <a href="/settings/plugins" 
           hx-get="/api/settings/plugins" 
           hx-target="#main-content">
    
    Note: This is marked as "founder-only" in the UI
    """
    settings_file = SETTINGS_DIR / "plugins.html"
    
    if not settings_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Plugins settings page not found at {settings_file}"
        )
    
    return FileResponse(settings_file, media_type="text/html")


@router.get("/api")
async def api_settings_page():
    """
    Serve API Settings page HTML.
    
    Route in index.html:
        <a href="/settings/api" 
           hx-get="/api/settings/api" 
           hx-target="#main-content">
    """
    settings_file = SETTINGS_DIR / "api.html"
    
    if not settings_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"API settings page not found at {settings_file}"
        )
    
    return FileResponse(settings_file, media_type="text/html")


# ============================================================================
# ICP SETTINGS API ENDPOINTS (USE SNIPER PLUGIN)
# ============================================================================

@router.get("/icp/data")
async def get_icp_settings(request: Request):
    """
    Get current ICP settings from Sniper plugin via dodman-core.
    
    Proxies to: GET /api/tenants/{tenant_id}/plugins/sniper/icp
    """
    try:
        tenant_id = get_tenant_id(request)
        headers = get_auth_header(request)
        
        # Proxy to dodman-core Sniper plugin ICP endpoint
        endpoint = f"/api/tenants/{tenant_id}/plugins/sniper/icp"
        result = await proxy_to_core(endpoint, method="GET", headers=headers)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ICP settings: {e}")
        # Return empty ICP as fallback
        return {
            "icp": {
                "industry": "",
                "company_size": "",
                "revenue_range": "",
                "funding_stage": "",
                "regions": [],
                "countries": "",
                "signals": [],
                "include_keywords": "",
                "exclude_keywords": ""
            }
        }



@router.post("/icp/data")
async def save_icp_settings(settings: ICPSettings, request: Request):
    """
    Save ICP settings to Sniper plugin via dodman-core.
    
    Proxies to: POST /api/tenants/{tenant_id}/plugins/sniper/icp
    """
    try:
        tenant_id = get_tenant_id(request)
        headers = get_auth_header(request)
        
        # Proxy to dodman-core Sniper plugin ICP update endpoint
        endpoint = f"/api/tenants/{tenant_id}/plugins/sniper/icp"
        result = await proxy_to_core(
            endpoint,
            method="POST",
            data=settings.dict(),
            headers=headers
        )
        
        return {
            "status": "success",
            "message": "ICP settings saved successfully",
            "settings": settings.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save ICP settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PLUGIN SETTINGS API ENDPOINTS
# ============================================================================

@router.get("/plugins/status")
async def get_plugins_status(request: Request):
    """
    Get status of all plugins via dodman-core.
    
    Makes 3 parallel requests to:
    - GET /api/tenants/{tenant_id}/plugins/sniper/status
    - GET /api/tenants/{tenant_id}/plugins/shadow/status
    - GET /api/tenants/{tenant_id}/plugins/ghost/status
    """
    try:
        tenant_id = get_tenant_id(request)
        headers = get_auth_header(request)
        
        plugins_list = []
        
        # Get status for each plugin via dodman-core
        for plugin_name in ['sniper', 'shadow', 'ghost']:
            try:
                endpoint = f"/api/tenants/{tenant_id}/plugins/{plugin_name}/status"
                status_result = await proxy_to_core(endpoint, method="GET", headers=headers)
                
                plugins_list.append({
                    "id": plugin_name,
                    "name": status_result.get('plugin_name', plugin_name).title(),
                    "version": "0.1.0",  # Get from status if available
                    "enabled": status_result.get('status') == 'active',
                    "status": status_result.get('status', 'unknown'),
                    "stats": status_result.get('stats', {}),
                    "last_run": status_result.get('last_run')
                })
                
            except Exception as e:
                logger.error(f"Failed to get {plugin_name} status: {e}")
                # Add plugin with error status
                plugins_list.append({
                    "id": plugin_name,
                    "name": plugin_name.title(),
                    "version": "unknown",
                    "enabled": False,
                    "status": "error",
                    "stats": {},
                    "last_run": None,
                    "error": str(e)
                })
        
        return {"plugins": plugins_list}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugins status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plugins/{plugin_name}/toggle")
async def toggle_plugin(plugin_name: str, toggle: PluginToggleRequest, request: Request):
    """
    Toggle plugin on/off (pause/resume) via dodman-core.
    
    Proxies to:
    - POST /api/tenants/{tenant_id}/plugins/{plugin_name}/pause
    - POST /api/tenants/{tenant_id}/plugins/{plugin_name}/resume
    """
    try:
        tenant_id = get_tenant_id(request)
        headers = get_auth_header(request)
        
        # Determine action
        action = "resume" if toggle.enabled else "pause"
        
        # Proxy to dodman-core
        endpoint = f"/api/tenants/{tenant_id}/plugins/{plugin_name}/{action}"
        result = await proxy_to_core(endpoint, method="POST", headers=headers)
        
        return {
            "status": "success",
            "message": f"Plugin {plugin_name} {'enabled' if toggle.enabled else 'paused'}",
            "plugin_status": result.get('status')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle {plugin_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API KEYS MANAGEMENT (LOCAL - NOT IN DODMAN-CORE)
# ============================================================================
# Note: API keys are managed locally in the dashboard, not in dodman-core
# This is intentional - each dashboard instance manages its own API keys

# Simple in-memory storage (use database in production)
_api_keys_storage: Dict[str, List[dict]] = {}


@router.get("/api/keys")
async def get_api_keys(request: Request):
    """
    Get all API keys for current tenant.
    
    Note: This is local storage, not proxied to dodman-core.
    API keys are scoped to the dashboard instance.
    """
    try:
        tenant_id = get_tenant_id(request)
        
        # Get keys for tenant
        keys = _api_keys_storage.get(tenant_id, [])
        
        # Mask actual keys (only show prefix)
        masked_keys = []
        for key in keys:
            masked_keys.append({
                "id": key['id'],
                "name": key['name'],
                "prefix": key['prefix'],
                "created_at": key['created_at'],
                "last_used": key.get('last_used'),
                "permissions": key['permissions'],
                "status": key['status']
            })
        
        return {"keys": masked_keys}
        
    except Exception as e:
        logger.error(f"Failed to get API keys: {e}")
        return {"keys": []}


@router.post("/api/keys")
async def create_api_key(
    name: str,
    permissions: str = "read_only",
    environment: str = "development",
    request: Request = None
):
    """
    Create a new API key.
    
    Note: Stored locally, not in dodman-core.
    """
    try:
        tenant_id = get_tenant_id(request)
        
        # Generate secure key
        key_prefix = "sk_prod_" if environment == "production" else "sk_test_"
        key_secret = secrets.token_urlsafe(32)
        full_key = f"{key_prefix}{key_secret}"
        key_id = f"key_{secrets.token_hex(8)}"
        
        from datetime import datetime
        
        # Create new key
        new_key = {
            "id": key_id,
            "name": name,
            "key": full_key,
            "prefix": key_prefix,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "permissions": permissions,
            "environment": environment,
            "status": "active"
        }
        
        # Store key
        if tenant_id not in _api_keys_storage:
            _api_keys_storage[tenant_id] = []
        
        _api_keys_storage[tenant_id].append(new_key)
        
        return {
            "status": "success",
            "message": "API key created successfully",
            "key": full_key,
            "key_id": key_id,
            "warning": "⚠️ Save this key now! It won't be shown again."
        }
        
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/keys/{key_id}")
async def revoke_api_key(key_id: str, request: Request):
    """Revoke an API key."""
    try:
        tenant_id = get_tenant_id(request)
        
        if tenant_id not in _api_keys_storage:
            raise HTTPException(status_code=404, detail="No API keys found")
        
        # Find and remove key
        keys = _api_keys_storage[tenant_id]
        updated_keys = [k for k in keys if k['id'] != key_id]
        
        if len(updated_keys) == len(keys):
            raise HTTPException(status_code=404, detail="API key not found")
        
        _api_keys_storage[tenant_id] = updated_keys
        
        return {
            "status": "success",
            "message": f"API key {key_id} revoked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBHOOKS MANAGEMENT (LOCAL)
# ============================================================================

# Simple in-memory storage (use database in production)
_webhooks_storage: Dict[str, List[dict]] = {}


@router.get("/api/webhooks")
async def get_webhooks(request: Request):
    """Get all configured webhooks."""
    try:
        tenant_id = get_tenant_id(request)
        webhooks = _webhooks_storage.get(tenant_id, [])
        
        return {"webhooks": webhooks}
        
    except Exception as e:
        logger.error(f"Failed to get webhooks: {e}")
        return {"webhooks": []}


@router.post("/api/webhooks")
async def create_webhook(
    name: str,
    url: str,
    events: List[str],
    request: Request = None
):
    """Create a new webhook."""
    try:
        tenant_id = get_tenant_id(request)
        
        webhook_id = f"webhook_{secrets.token_hex(8)}"
        
        from datetime import datetime
        
        new_webhook = {
            "id": webhook_id,
            "name": name,
            "url": url,
            "events": events,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_triggered": None
        }
        
        if tenant_id not in _webhooks_storage:
            _webhooks_storage[tenant_id] = []
        
        _webhooks_storage[tenant_id].append(new_webhook)
        
        return {
            "status": "success",
            "message": "Webhook created successfully",
            "webhook": new_webhook
        }
        
    except Exception as e:
        logger.error(f"Failed to create webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: str, request: Request):
    """Send a test event to a webhook."""
    try:
        tenant_id = get_tenant_id(request)
        
        if tenant_id not in _webhooks_storage:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        webhook = next(
            (w for w in _webhooks_storage[tenant_id] if w['id'] == webhook_id),
            None
        )
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        from datetime import datetime
        
        # Send test payload
        test_payload = {
            "event": "test",
            "tenant_id": tenant_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "message": "This is a test webhook event"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook['url'],
                json=test_payload,
                timeout=10.0
            )
        
        return {
            "status": "success",
            "message": "Test webhook sent successfully",
            "response_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def settings_health():
    """
    Check if all settings pages exist and dodman-core is reachable.
    """
    pages = {
        "icp": (SETTINGS_DIR / "icp.html").exists(),
        "plugins": (SETTINGS_DIR / "plugins.html").exists(),
        "api": (SETTINGS_DIR / "api.html").exists()
    }
    
    # Check dodman-core connectivity
    core_reachable = False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DODMAN_CORE_API_URL}/health", timeout=5.0)
            core_reachable = response.status_code == 200
    except:
        pass
    
    all_healthy = all(pages.values()) and core_reachable
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "settings_dir": str(SETTINGS_DIR),
        "pages": pages,
        "dodman_core": {
            "url": DODMAN_CORE_API_URL,
            "reachable": core_reachable
        }
    }
