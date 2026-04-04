"""
Plugin Dashboard Routes

Serves plugin HTML dashboards for HTMX integration.
Separate from API proxy routes in plugins.py
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

# Create router
router = APIRouter(prefix="/plugins", tags=["Plugin Dashboards"])

# Get frontend directory path
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
PLUGINS_DIR = FRONTEND_DIR / "plugins"


# ============================================================================
# PLUGIN DASHBOARD ROUTES (HTMX)
# ============================================================================

@router.get("/sniper/dashboard")
async def sniper_dashboard():
    """
    Serve AI Lead Sniper plugin dashboard HTML.
    
    This endpoint is called by HTMX when user clicks "Lead Sniper" in sidebar.
    Returns HTML content that gets injected into #main-content.
    
    Route in index.html:
        <a href="/plugins/sniper" 
           hx-get="/api/plugins/sniper/dashboard" 
           hx-target="#main-content">
    """
    plugin_file = PLUGINS_DIR / "sniper.html"
    
    if not plugin_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Sniper plugin not found at {plugin_file}"
        )
    
    return FileResponse(plugin_file, media_type="text/html")


@router.get("/shadow/dashboard")
async def shadow_dashboard():
    """
    Serve Competitor Shadow plugin dashboard HTML.
    
    This endpoint is called by HTMX when user clicks "Shadow Intelligence" in sidebar.
    Returns HTML content that gets injected into #main-content.
    
    Route in index.html:
        <a href="/plugins/shadow" 
           hx-get="/api/plugins/shadow/dashboard" 
           hx-target="#main-content">
    """
    plugin_file = PLUGINS_DIR / "shadow.html"
    
    if not plugin_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Shadow plugin not found at {plugin_file}"
        )
    
    return FileResponse(plugin_file, media_type="text/html")


@router.get("/ghost/dashboard")
async def ghost_dashboard():
    """
    Serve Ghost Writer plugin dashboard HTML.
    
    This endpoint is called by HTMX when user clicks "Ghost Writer" in sidebar.
    Returns HTML content that gets injected into #main-content.
    
    Route in index.html:
        <a href="/plugins/ghost" 
           hx-get="/api/plugins/ghost/dashboard" 
           hx-target="#main-content">
    """
    plugin_file = PLUGINS_DIR / "ghost.html"
    
    if not plugin_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Ghost plugin not found at {plugin_file}"
        )
    
    return FileResponse(plugin_file, media_type="text/html")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/dashboards/health")
async def dashboards_health():
    """
    Check if all plugin dashboard files exist.
    
    Useful for debugging plugin setup.
    """
    plugins = {
        "sniper": {
            "path": str(PLUGINS_DIR / "sniper.html"),
            "exists": (PLUGINS_DIR / "sniper.html").exists()
        },
        "shadow": {
            "path": str(PLUGINS_DIR / "shadow.html"),
            "exists": (PLUGINS_DIR / "shadow.html").exists()
        },
        "ghost": {
            "path": str(PLUGINS_DIR / "ghost.html"),
            "exists": (PLUGINS_DIR / "ghost.html").exists()
        }
    }
    
    all_healthy = all(p["exists"] for p in plugins.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "plugins_dir": str(PLUGINS_DIR),
        "plugins": plugins
    }