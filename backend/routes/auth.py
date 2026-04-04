"""
Dashboard Authentication Routes

Handles dashboard-specific auth flows (login, logout, session management)
while proxying to dodman-core API.
"""

from fastapi import APIRouter, HTTPException, status, Response, Cookie
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

DODMAN_CORE_API_URL = os.getenv("DODMAN_CORE_API_URL", "http://localhost:8080")



# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request with email or subdomain"""
    email: Optional[EmailStr] = None
    subdomain: Optional[str] = None


class LoginResponse(BaseModel):
    """Response after requesting magic link"""
    success: bool
    message: str
    sent_to: str


class VerifyTokenRequest(BaseModel):
    """Verify magic link token"""
    token: str


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/login", response_model=LoginResponse)
async def request_magic_link(request: LoginRequest):
    """
    Request magic link for dashboard login.
    
    Proxies to dodman-core API /api/auth/request-magic-link
    
    Args:
        request: Email or subdomain
    
    Returns:
        Success message with recipient email
    """
    try:
        # Proxy to dodman-core API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DODMAN_CORE_API_URL}/api/auth/request-magic-link",
                json=request.dict(exclude_none=True),
                timeout=10.0
            )
        
        if response.status_code != 200:
            error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("detail", "Failed to send magic link")
            )
        
        data = response.json()
        
        return LoginResponse(
            success=True,
            message="Magic link sent! Check your email.",
            sent_to=data.get("sent_to", "your email")
        )
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


@router.post("/verify")
async def verify_magic_link(
    request: VerifyTokenRequest,
    response: Response
):
    """
    Verify magic link token and create session.
    
    Proxies to dodman-core API /api/auth/verify-magic-link
    
    Args:
        request: Magic link token
        response: Response object (to set cookies)
    
    Returns:
        User data and session tokens
    """
    try:
        # Proxy to dodman-core API
        async with httpx.AsyncClient() as client:
            api_response = await client.post(
                f"{DODMAN_CORE_API_URL}/api/auth/verify-magic-link",
                json=request.dict(),
                timeout=10.0
            )
        
        if api_response.status_code != 200:
            error_data = api_response.json()
            raise HTTPException(
                status_code=api_response.status_code,
                detail=error_data.get("detail", "Invalid or expired magic link")
            )
        
        data = api_response.json()
        
        # Set secure session cookie
        response.set_cookie(
            key="session_token",
            value=data["session_token"],
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=data["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=30 * 24 * 60 * 60  # 30 days
        )
        
        return {
            "success": True,
            "user": data["user"],
            "message": "Login successful"
        }
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


@router.post("/logout")
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None)
):
    """
    Logout user and invalidate session.
    
    Args:
        response: Response object (to clear cookies)
        session_token: Session token from cookie
    
    Returns:
        Success message
    """
    try:
        # If we have a session token, invalidate it on the server
        if session_token:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{DODMAN_CORE_API_URL}/api/auth/logout",
                    headers={"Authorization": f"Bearer {session_token}"},
                    timeout=5.0
                )
        
        # Clear cookies
        response.delete_cookie("session_token")
        response.delete_cookie("refresh_token")
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    
    except httpx.RequestError:
        # Even if API fails, clear local cookies
        response.delete_cookie("session_token")
        response.delete_cookie("refresh_token")
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }


@router.post("/refresh")
async def refresh_session(
    response: Response,
    refresh_token: Optional[str] = Cookie(None)
):
    """
    Refresh session token using refresh token.
    
    Args:
        response: Response object (to update cookies)
        refresh_token: Refresh token from cookie
    
    Returns:
        New session token
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    try:
        # Proxy to dodman-core API
        async with httpx.AsyncClient() as client:
            api_response = await client.post(
                f"{DODMAN_CORE_API_URL}/api/auth/refresh-token",
                json={"refresh_token": refresh_token},
                timeout=10.0
            )
        
        if api_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        data = api_response.json()
        
        # Update session cookie
        response.set_cookie(
            key="session_token",
            value=data["session_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )
        
        return {
            "success": True,
            "message": "Session refreshed"
        }
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


@router.get("/session")
async def get_session(session_token: Optional[str] = Cookie(None)):
    """
    Get current session info.
    
    Args:
        session_token: Session token from cookie
    
    Returns:
        Session status and user info
    """
    if not session_token:
        return {
            "authenticated": False,
            "user": None
        }
    
    try:
        # TODO: Decode JWT locally or proxy to dodman-core
        # For now, just return that user is authenticated
        return {
            "authenticated": True,
            "message": "Session valid"
        }
    
    except Exception:
        return {
            "authenticated": False,
            "user": None
        }