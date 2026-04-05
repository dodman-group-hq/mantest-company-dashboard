/**
 * Dodman Dashboard — Auth Guard
 * Path: /frontend/js/auth.js
 *
 * Handles:
 * 1. Auth guard  — verifies session token on every page load, redirects to
 *                  login if missing or expired, tries refresh before giving up
 * 2. Placeholder population — fills {{CLIENT_NAME}}, {{USER_NAME}},
 *                  {{USER_INITIALS}}, {{USER_ROLE}} from the session token
 * 3. Logout      — clears tokens and redirects to ai.dodman.group/login.html
 * 4. Fetch patch — attaches Authorization header to all dodman-core API calls
 */

const AUTH = (() => {
    const CORE_API    = 'https://dodman-core.onrender.com';
    const LOGIN_URL   = 'https://ai.dodman.group/login.html';
    const SESSION_KEY = 'dodman_session_token';
    const REFRESH_KEY = 'dodman_refresh_token';
    const TENANT_KEY  = 'dodman_tenant_id';

    function getSessionToken() { return sessionStorage.getItem(SESSION_KEY); }
    function getRefreshToken() { return sessionStorage.getItem(REFRESH_KEY); }

    function clearTokens() {
        sessionStorage.removeItem(SESSION_KEY);
        sessionStorage.removeItem(REFRESH_KEY);
        sessionStorage.removeItem(TENANT_KEY);
        sessionStorage.removeItem('dodman_subdomain');
    }

    function decodeJWT(token) {
        try {
            const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(atob(base64));
        } catch { return null; }
    }

    function isTokenExpired(token) {
        const payload = decodeJWT(token);
        if (!payload || !payload.exp) return true;
        return (payload.exp * 1000) < (Date.now() + 30_000);
    }

    async function refreshSession() {
        const refreshToken = getRefreshToken();
        if (!refreshToken || isTokenExpired(refreshToken)) return false;
        try {
            const res = await fetch(`${CORE_API}/api/auth/refresh-token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (!res.ok) return false;
            const data = await res.json();
            if (data.session_token) {
                sessionStorage.setItem(SESSION_KEY, data.session_token);
                return true;
            }
            return false;
        } catch { return false; }
    }

    function redirectToLogin(reason = '') {
        clearTokens();
        const url = reason ? `${LOGIN_URL}?error=${encodeURIComponent(reason)}` : LOGIN_URL;
        window.location.href = url;
    }

    async function logout() {
        const token = getSessionToken();
        if (token) {
            try {
                await fetch(`${CORE_API}/api/auth/logout`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                });
            } catch { /* best-effort */ }
        }
        redirectToLogin();
    }

    function populatePlaceholders(payload) {
        const tenantName = sessionStorage.getItem('dodman_tenant_name') || 'Dashboard';
        const email      = payload.email || '';
        const userName   = email.split('@')[0] || tenantName;
        const role       = payload.role || 'Admin';
        const initials   = userName.slice(0, 2).toUpperCase();

        function replaceInNode(node, placeholder, value) {
            if (node.nodeType === Node.TEXT_NODE) {
                if (node.textContent.includes(placeholder)) {
                    node.textContent = node.textContent.replaceAll(placeholder, value);
                }
            } else {
                node.childNodes.forEach(child => replaceInNode(child, placeholder, value));
            }
        }

        const replacements = {
            '{{CLIENT_NAME}}':   tenantName,
            '{{USER_NAME}}':     userName,
            '{{USER_INITIALS}}': initials,
            '{{USER_ROLE}}':     role,
        };

        Object.entries(replacements).forEach(([placeholder, value]) => {
            replaceInNode(document.body, placeholder, value);
            if (document.title.includes(placeholder)) {
                document.title = document.title.replaceAll(placeholder, value);
            }
        });
    }

    function _patchFetch(token) {
        const _origFetch = window.fetch;
        window.fetch = function (url, options = {}) {
            if (typeof url === 'string') {
                // Attach token to:
                // 1. Direct dodman-core calls (from plugin JS)
                // 2. Local /api/ calls (proxied through the dashboard backend)
                const isDodmanCore = url.includes('dodman-core.onrender.com');
                const isLocalApi   = url.startsWith('/api/') || url.startsWith('api/');
                if (isDodmanCore || isLocalApi) {
                    options = { ...options };
                    options.headers = {
                        ...options.headers,
                        'Authorization': `Bearer ${token}`,
                    };
                }
            }
            return _origFetch(url, options);
        };
    }

    async function requireAuth() {
        if (window.location.pathname.startsWith('/auth/callback')
            || window.location.pathname.startsWith('/auth/verify')) {
            return;
        }

        let token = getSessionToken();

        if (!token) { redirectToLogin('session_expired'); return; }

        if (isTokenExpired(token)) {
            const refreshed = await refreshSession();
            if (!refreshed) { redirectToLogin('session_expired'); return; }
            token = getSessionToken();
        }

        _patchFetch(token);

        const payload = decodeJWT(token);
        if (payload) populatePlaceholders(payload);

        document.querySelectorAll('a[href="/logout"], [data-action="logout"]').forEach(el => {
            el.addEventListener('click', (e) => { e.preventDefault(); logout(); });
        });
    }

    return { requireAuth, logout, getSessionToken, decodeJWT };
})();

document.addEventListener('DOMContentLoaded', () => AUTH.requireAuth());