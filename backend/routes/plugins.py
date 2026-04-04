"""
Plugin Routes

Handles plugin management, execution, and sandbox environments.
"""

from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import os

router = APIRouter(prefix="/plugins", tags=["Plugins"])

DODMAN_CORE_API_URL = os.getenv("DODMAN_CORE_API_URL", "http://localhost:8000")
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PluginExecuteRequest(BaseModel):
    """Execute plugin request"""
    plugin_id: str
    action: str
    payload: Dict[str, Any]


class PluginConfigUpdate(BaseModel):
    """Update plugin configuration"""
    config: Dict[str, Any]


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/")
async def list_plugins(authorization: Optional[str] = Header(None)):
    """
    List all available plugins for current tenant.
    
    Proxies to dodman-core /api/plugins
    """
    try:
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DODMAN_CORE_API_URL}/api/plugins",
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch plugins"
            )
        
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plugin service unavailable"
        )


@router.get("/{plugin_id}")
async def get_plugin(
    plugin_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get detailed information about a specific plugin.
    
    Args:
        plugin_id: Plugin identifier (e.g., 'sniper', 'mirror')
        authorization: JWT session token
    
    Returns:
        Plugin details, status, configuration
    """
    try:
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DODMAN_CORE_API_URL}/api/plugins/{plugin_id}",
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Plugin '{plugin_id}' not found"
            )
        
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plugin service unavailable"
        )


@router.post("/{plugin_id}/execute")
async def execute_plugin(
    plugin_id: str,
    request: PluginExecuteRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Execute a plugin action.
    
    Args:
        plugin_id: Plugin identifier
        request: Execution request with action and payload
        authorization: JWT session token
    
    Returns:
        Plugin execution result
    """
    try:
        headers = {"Content-Type": "application/json"}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DODMAN_CORE_API_URL}/api/plugins/{plugin_id}/execute",
                json=request.dict(),
                headers=headers,
                timeout=30.0  # Longer timeout for plugin execution
            )
        
        if response.status_code != 200:
            error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("detail", "Plugin execution failed")
            )
        
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plugin service unavailable"
        )


@router.get("/{plugin_id}/status")
async def get_plugin_status(
    plugin_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get plugin status and metrics.
    
    Args:
        plugin_id: Plugin identifier
        authorization: JWT session token
    
    Returns:
        Plugin status, last run, metrics
    """
    try:
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DODMAN_CORE_API_URL}/api/plugins/{plugin_id}/status",
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch plugin status"
            )
        
        return response.json()
    
    except httpx.RequestError:
        # Return mock status if API unavailable
        return {
            "plugin_id": plugin_id,
            "status": "unknown",
            "message": "Plugin service unavailable"
        }


@router.put("/{plugin_id}/config")
async def update_plugin_config(
    plugin_id: str,
    request: PluginConfigUpdate,
    authorization: Optional[str] = Header(None)
):
    """
    Update plugin configuration.
    
    Args:
        plugin_id: Plugin identifier
        request: New configuration
        authorization: JWT session token
    
    Returns:
        Updated configuration
    """
    try:
        headers = {"Content-Type": "application/json"}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{DODMAN_CORE_API_URL}/api/plugins/{plugin_id}/config",
                json=request.dict(),
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code != 200:
            error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("detail", "Failed to update configuration")
            )
        
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plugin service unavailable"
        )


@router.post("/{plugin_id}/pause")
async def pause_plugin(
    plugin_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Pause plugin execution.
    
    Args:
        plugin_id: Plugin identifier
        authorization: JWT session token
    
    Returns:
        Success status
    """
    try:
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DODMAN_CORE_API_URL}/api/plugins/{plugin_id}/pause",
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to pause plugin"
            )
        
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plugin service unavailable"
        )


@router.post("/{plugin_id}/resume")
async def resume_plugin(
    plugin_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Resume plugin execution.
    
    Args:
        plugin_id: Plugin identifier
        authorization: JWT session token
    
    Returns:
        Success status
    """
    try:
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DODMAN_CORE_API_URL}/api/plugins/{plugin_id}/resume",
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to resume plugin"
            )
        
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Plugin service unavailable"
        )


@router.get("/sniper/dashboard")
async def sniper_dashboard():
    """Serve Sniper plugin HTML"""
    return FileResponse(FRONTEND_DIR / "plugins" / "sniper.html")

@router.get("/shadow/dashboard")
async def shadow_dashboard():
    """Serve Shadow plugin HTML"""
    return FileResponse(FRONTEND_DIR / "plugins" / "shadow.html")

@router.get("/ghost/dashboard")
async def ghost_dashboard():
    """Serve Ghost Writer plugin HTML"""
    return FileResponse(FRONTEND_DIR / "plugins" / "ghost.html")