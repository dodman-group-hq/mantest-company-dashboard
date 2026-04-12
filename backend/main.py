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
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import httpx
import os
import asyncio
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
# HELPERS
# ============================================================================

def _extract_tenant_id(authorization: Optional[str]) -> Optional[str]:
    """Extract tenant_id from a Bearer JWT without full verification."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        import base64, json as _json
        token = authorization.split(" ", 1)[1]
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("tenant_id")
    except Exception:
        return None

# ============================================================================
# PLUGIN MANAGEMENT
# ============================================================================

@app.get("/api/dashboard/plugins")
async def list_available_plugins(authorization: Optional[str] = Header(None)):
    """
    List all plugins and their live status.
    Fetches status for each known plugin from dodman-core.
    """
    tenant_id = _extract_tenant_id(authorization)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    known_plugins = [
        {"id": "sniper", "name": "Lead Sniper",         "icon": "🎯", "category": "intelligence"},
        {"id": "shadow", "name": "Shadow Intelligence", "icon": "👁️", "category": "intelligence"},
        {"id": "ghost",  "name": "Ghost Writer",        "icon": "✍️", "category": "content"},
    ]

    results = []
    async with httpx.AsyncClient() as client:
        for p in known_plugins:
            try:
                resp = await client.get(
                    f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}/plugins/{p['id']}/status",
                    headers={"Authorization": authorization},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results.append({
                        **p,
                        "status":     data.get("status", "unknown"),
                        "last_run":   data.get("last_run"),
                        "runs_today": data.get("stats", {}).get("runs_today", 0),
                    })
                else:
                    results.append({**p, "status": "not_installed"})
            except Exception as e:
                logger.warning(f"Could not get status for plugin {p['id']}: {e}")
                results.append({**p, "status": "unavailable"})

    return {"plugins": results}


@app.get("/api/dashboard/plugin/{plugin_id}")
async def get_plugin_details(plugin_id: str, authorization: Optional[str] = Header(None)):
    """
    Get detailed status and metrics for a specific plugin.
    """
    tenant_id = _extract_tenant_id(authorization)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}/plugins/{plugin_id}/status",
                headers={"Authorization": authorization},
                timeout=10.0
            )

        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch plugin details")

        data = resp.json()
        stats = data.get("stats", {})

        return {
            "plugin": {
                "id":      plugin_id,
                "name":    data.get("plugin_name", plugin_id.capitalize()),
                "status":  data.get("status", "unknown"),
                "last_run": data.get("last_run"),
                "metrics": {
                    "runs_today":   stats.get("runs_today", 0),
                    "leads_found":  stats.get("leads_found", 0),
                    "api_cost_usd": stats.get("api_cost_usd", 0.0),
                    "success_rate": data.get("success_rate", 100),
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plugin details for {plugin_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch plugin details")


# ============================================================================
# DASHBOARD DATA
# ============================================================================

@app.get("/api/dashboard/overview", response_class=HTMLResponse)
async def get_dashboard_overview(request: Request, authorization: Optional[str] = Header(None)):
    """
    Get dashboard overview as an HTML fragment for HTMX.
    Fetches real data from dodman-core and renders the stats cards.
    """
    # Extract tenant_id from the JWT in the Authorization header
    tenant_id = None
    total_leads = 0
    api_usage = "$0.00"
    active_plugins = 0

    tenant_id = _extract_tenant_id(authorization)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if tenant_id:
        try:
            async with httpx.AsyncClient() as client:
                # Fetch leads count
                leads_resp = await client.get(
                    f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}/plugins/sniper/leads",
                    headers={"Authorization": authorization},
                    params={"limit": 1000, "min_score": 0},
                    timeout=10.0
                )
                if leads_resp.status_code == 200:
                    leads_data = leads_resp.json()
                    total_leads = leads_data.get("total", 0)

                # Fetch tenant info for API usage
                tenant_resp = await client.get(
                    f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}",
                    headers={"Authorization": authorization},
                    timeout=10.0
                )
                if tenant_resp.status_code == 200:
                    tenant_data = tenant_resp.json()
                    cost = tenant_data.get("api_usage_cost", 0)
                    api_usage = f"${float(cost):.2f}"

                # Check plugin statuses
                plugin_count = 0
                for plugin in ["sniper", "shadow", "ghost"]:
                    status_resp = await client.get(
                        f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}/plugins/{plugin}/status",
                        headers={"Authorization": authorization},
                        timeout=5.0
                    )
                    if status_resp.status_code == 200:
                        pdata = status_resp.json()
                        if pdata.get("status") not in ("not_installed", "error"):
                            plugin_count += 1
                active_plugins = plugin_count
        except Exception as e:
            logger.warning(f"Failed to fetch overview data: {e}")

    html = f"""
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-sm border border-[var(--border-color)] p-6">
            <div class="flex items-center justify-between mb-2">
                <p class="text-sm text-[var(--text-secondary)]">Leads Found</p>
                <svg class="w-5 h-5 text-[var(--accent)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
            </div>
            <p class="text-3xl font-bold text-[var(--text-main)]">{total_leads}</p>
            <p class="text-xs text-[var(--text-muted)] mt-1">Total in vault</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-[var(--border-color)] p-6">
            <div class="flex items-center justify-between mb-2">
                <p class="text-sm text-[var(--text-secondary)]">Active Plugins</p>
                <svg class="w-5 h-5 text-[var(--success)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            </div>
            <p class="text-3xl font-bold text-[var(--text-main)]">{active_plugins}</p>
            <p class="text-xs text-[var(--text-muted)] mt-1">Sniper, Shadow, Ghost</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-[var(--border-color)] p-6">
            <div class="flex items-center justify-between mb-2">
                <p class="text-sm text-[var(--text-secondary)]">API Usage</p>
                <svg class="w-5 h-5 text-[var(--info)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
            </div>
            <p class="text-3xl font-bold text-[var(--text-main)]">{api_usage}</p>
            <p class="text-xs text-[var(--text-muted)] mt-1">Today</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-[var(--border-color)] p-6">
            <div class="flex items-center justify-between mb-2">
                <p class="text-sm text-[var(--text-secondary)]">Core Health</p>
                <div class="w-2 h-2 bg-[var(--success)] rounded-full animate-pulse"></div>
            </div>
            <p class="text-3xl font-bold text-[var(--text-main)]">100%</p>
            <p class="text-xs text-[var(--text-muted)] mt-1">All systems operational</p>
        </div>
    </div>
    <div class="bg-white rounded-lg shadow-sm border border-[var(--border-color)] p-6">
        <h2 class="text-xl font-semibold text-[var(--text-main)] mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button onclick="window.location.href='/plugins/sniper'" class="flex items-center justify-center px-6 py-4 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition-opacity">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                Run Scour
            </button>
            <button onclick="window.location.href='/plugins/shadow'" class="flex items-center justify-center px-6 py-4 bg-white border-2 border-[var(--accent)] text-[var(--accent)] rounded-lg hover:bg-[var(--accent-light)] transition-colors">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                Add Competitor
            </button>
            <button onclick="window.location.href='/plugins/ghost'" class="flex items-center justify-center px-6 py-4 bg-white border border-[var(--border-color)] text-[var(--text-main)] rounded-lg hover:bg-[var(--bg-hover)] transition-colors">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                View Reports
            </button>
        </div>
    </div>
    """
    return HTMLResponse(content=html)


# ============================================================================
# SETTINGS DATA ENDPOINTS (JSON) — separate from the HTML fragment endpoints
# ============================================================================
# The HTML fragment endpoints (in routes/settings.py) serve the page shell
# for HTMX. These endpoints serve the *data* as JSON so plugin scripts can
# call apiRequest('/api/settings/icp/data') and get back structured data
# rather than HTML, which would cause "Non-JSON response" errors in global.js.

@app.get("/api/settings/icp/data")
async def get_icp_data(authorization: Optional[str] = Header(None)):
    """Return the tenant's saved ICP profile as JSON."""
    tenant_id = _extract_tenant_id(authorization)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}/icp",
                headers={"Authorization": authorization},
                timeout=10.0
            )
        if resp.status_code == 404:
            return {"icp": {}}
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch ICP data")
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ICP data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch ICP data")


@app.get("/api/settings/api/data")
async def get_api_settings_data(authorization: Optional[str] = Header(None)):
    """Return the tenant's API keys/settings as JSON."""
    tenant_id = _extract_tenant_id(authorization)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{DODMAN_CORE_API_URL}/api/tenants/{tenant_id}/api-keys",
                headers={"Authorization": authorization},
                timeout=10.0
            )
        if resp.status_code == 404:
            return {"api_keys": []}
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch API settings")
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching API settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch API settings")


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

        # Tell dodman-core not to compress its response — the GZipMiddleware
        # on this server will handle compression for the browser. Without this,
        # httpx decompresses the gzip body but the original Content-Encoding
        # header is still forwarded, causing the browser to try to decompress
        # already-plain data and get garbage bytes.
        headers["accept-encoding"] = "identity"

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
async def keep_core_awake():
    while True:
        await asyncio.sleep(600)  # every 10 minutes
        try:
            async with httpx.AsyncClient() as client:
                await client.get(f"{DODMAN_CORE_API_URL}/api/health", timeout=10.0)
                logger.info("Core API keepalive ping sent")
        except Exception:
            pass

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

    asyncio.create_task(keep_core_awake())


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