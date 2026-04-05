"""
Master Dashboard Template - Backend
FastAPI server that serves the frontend and proxies requests to dodman-core API.

Architecture:
- Serves static frontend files
- Proxies authenticated requests to dodman-core API
- Handles session management
- Provides sandbox environment for plugins
"""

from fastapi import FastAPI, Request, HTTPException, status, Header, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import httpx
import os
from pathlib import Path
from typing import Optional
import logging

# Import route modules
from routes import auth, plugins, plugin_dashboards, settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Master Dashboard Template",
    description="Universal multi-tenant dashboard frontend + proxy",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuration
DODMAN_CORE_API_URL = os.getenv("DODMAN_CORE_API_URL", "https://dodman-core.onrender.com")
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============================================================================
# STATIC FILES
# ============================================================================

# Serve static files (CSS, JS, images)
app.mount("/css",          StaticFiles(directory=FRONTEND_DIR / "css"),    name="css")
app.mount("/js",           StaticFiles(directory=FRONTEND_DIR / "js"),     name="js")
# /frontend/js mirrors /js — index.html references /frontend/js/auth.js
app.mount("/frontend/js",  StaticFiles(directory=FRONTEND_DIR / "js"),     name="frontend_js")
app.mount("/frontend/css", StaticFiles(directory=FRONTEND_DIR / "css"),    name="frontend_css")
app.mount("/assets",       StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
app.mount("/admin",        StaticFiles(directory=FRONTEND_DIR / "admin"),  name="admin")

# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

# Register auth routes
app.include_router(auth.router, prefix="/api")

# Register plugin routes
app.include_router(plugins.router, prefix="/api")

# Register plugin dashboard routes
app.include_router(plugin_dashboards.router, prefix="/api")

# Register settings routes
app.include_router(settings.router, prefix="/api")

# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve main dashboard index.html"""
    index_file = FRONTEND_DIR / "index.html"
    
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
    
    return FileResponse(index_file)

@app.get("/verify", response_class=HTMLResponse)
async def serve_verify():
    """
    Serve verify.html when user clicks magic link from email.
    
    The magic link looks like:
    https://acme.dodman.ai/verify?token=eyJhbG...
    
    This route serves the verify.html page which extracts the token
    and verifies it with the API.
    """
    verify_file = FRONTEND_DIR / "verify.html"
    
    if not verify_file.exists():
        raise HTTPException(status_code=404, detail="Verify page not found")
    
    return FileResponse(verify_file)


@app.get("/auth/callback", response_class=HTMLResponse)
async def serve_auth_callback():
    """
    Receive the post-magic-link redirect from dodman-core.

    dodman-core redirects here after verifying the magic link:
        /auth/callback?session_token=...&refresh_token=...&tenant_id=...

    verify.html picks up the tokens from the URL, stores them in
    sessionStorage, strips them from the URL, then redirects to /.
    """
    verify_file = FRONTEND_DIR / "verify.html"
    if not verify_file.exists():
        raise HTTPException(status_code=404, detail="Verify page not found")
    return FileResponse(verify_file)


@app.get("/logout", response_class=HTMLResponse)
async def serve_logout():
    """
    Logout route — auth.js intercepts this client-side and calls the
    dodman-core logout API, then clears sessionStorage and redirects
    to the login page. This server route is a fallback for direct navigation.
    """
    # Redirect to login page directly
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="https://ai.dodman.group/login.html", status_code=302)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "master-dashboard-template",
        "version": "1.0.0",
        "core_api": DODMAN_CORE_API_URL
    }


# ============================================================================
# API PROXY TO DODMAN-CORE
# ============================================================================

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_core_api(
    path: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Proxy all /api/* requests to dodman-core API.
    
    This allows the frontend to make requests to /api/auth/*, /api/tenants/*, etc.
    and have them automatically forwarded to the core API.
    
    Args:
        path: API path (e.g., "auth/request-magic-link")
        request: Original request
        authorization: Authorization header (JWT token)
    
    Returns:
        Response from dodman-core API
    """
    try:
        # Get request body
        body = await request.body()

        # Forward all safe headers from the original request.
        # Critically this includes Authorization — without forwarding it
        # dodman-core rejects every proxied request with 401.
        # We skip hop-by-hop headers that must not be forwarded.
        HOP_BY_HOP = {
            'host', 'connection', 'keep-alive', 'transfer-encoding',
            'te', 'trailer', 'upgrade', 'proxy-authorization',
            'proxy-authenticate',
        }
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in HOP_BY_HOP
        }

        # Build full URL to dodman-core API
        target_url = f"{DODMAN_CORE_API_URL}/api/{path}"

        logger.info(f"Proxying {request.method} {path} -> {target_url}")

        # Make request to dodman-core API
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
        
        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    
    except httpx.ConnectError:
        logger.error(f"Failed to connect to dodman-core API: {DODMAN_CORE_API_URL}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Core API unavailable"
        )
    
    except Exception as e:
        logger.error(f"Proxy error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Proxy request failed"
        )


# ============================================================================
# PLUGIN MANAGEMENT
# ============================================================================

@app.get("/api/dashboard/plugins")
async def list_available_plugins():
    """
    List all available plugins for this tenant.
    
    Returns plugin metadata including name, description, icon, etc.
    """
    # TODO: Query dodman-core API for tenant's available plugins
    # For now, return mock data
    return {
        "plugins": [
            {
                "id": "sniper",
                "name": "Sniper",
                "description": "AI-powered lead capture engine",
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
            },
            {
                "id": "apollo",
                "name": "Apollo",
                "description": "Contact enrichment",
                "icon": "🚀",
                "category": "intelligence",
                "status": "inactive",
                "version": "1.0.0"
            }
        ]
    }


@app.get("/api/dashboard/plugin/{plugin_id}")
async def get_plugin_details(plugin_id: str):
    """Get detailed information about a specific plugin."""
    # TODO: Query dodman-core API
    return {
        "plugin": {
            "id": plugin_id,
            "name": plugin_id.capitalize(),
            "description": f"Details for {plugin_id} plugin",
            "status": "active",
            "metrics": {
                "total_runs": 0,
                "last_run": None,
                "success_rate": 100
            }
        }
    }


# ============================================================================
# DASHBOARD DATA
# ============================================================================

@app.get("/api/dashboard/overview")
async def get_dashboard_overview(authorization: Optional[str] = Header(None)):
    """
    Get dashboard overview data.
    
    Returns:
        Overview metrics, recent activity, alerts
    """
    # TODO: Proxy to dodman-core /api/tenants/overview
    return {
        "metrics": {
            "total_leads": 0,
            "active_plugins": 0,
            "api_usage": 0,
            "credit_remaining": 1000
        },
        "recent_activity": [],
        "alerts": []
    }


# ============================================================================
# SANDBOX ENVIRONMENT
# ============================================================================

@app.get("/sandbox/plugin/{plugin_id}", response_class=HTMLResponse)
async def serve_plugin_sandbox(plugin_id: str):
    """
    Serve sandbox environment for plugin development.
    
    Loads the plugin's sandbox template if it exists, otherwise
    serves the default sandbox.html.
    """
    # Check for plugin-specific sandbox template
    plugin_template = Path(__file__).parent / f"templates/plugins/{plugin_id}/sandbox.html"
    
    if plugin_template.exists():
        return FileResponse(plugin_template)
    
    # Fallback to default sandbox
    default_sandbox = FRONTEND_DIR / "admin" / "sandbox.html"
    
    if default_sandbox.exists():
        return FileResponse(default_sandbox)
    
    raise HTTPException(status_code=404, detail="Sandbox not found")


# ============================================================================
# CATCH-ALL — serve index.html for all unrecognised frontend routes
# ============================================================================
# Without this, refreshing on /plugins/sniper returns a 404 because FastAPI
# has no explicit route for it. With this, the server returns index.html,
# auth.js re-authenticates from sessionStorage, and HTMX re-fetches the
# correct plugin content. Must be registered AFTER all other routes.

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_catch_all(full_path: str, request: Request):
    """Serve index.html for all frontend routes so browser refresh works."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
    return FileResponse(index_file)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 handler"""
    logger.error(f"Internal error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info("Master Dashboard Template - Backend Starting")
    logger.info("=" * 60)
    logger.info(f"Frontend Directory: {FRONTEND_DIR}")
    logger.info(f"Core API URL: {DODMAN_CORE_API_URL}")
    logger.info(f"Serving at: http://localhost:3000")
    logger.info("=" * 60)
    
    # Verify frontend directory exists
    if not FRONTEND_DIR.exists():
        logger.warning(f"Frontend directory not found: {FRONTEND_DIR}")
    else:
        logger.info(f"✓ Frontend directory found")
    
    # Test connection to dodman-core API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DODMAN_CORE_API_URL}/health", timeout=5.0)
            if response.status_code == 200:
                logger.info(f"✓ Core API reachable")
            else:
                logger.warning(f"⚠ Core API returned {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠ Core API not reachable: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Master Dashboard Template shutting down...")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )