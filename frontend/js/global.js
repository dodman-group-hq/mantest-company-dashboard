/**
 * Sovereign Master Template - Global JavaScript
 * 
 * Shared UI logic for:
 * - Notifications
 * - Modals
 * - Sidebar toggling
 * - Breadcrumb updates
 * - Core status monitoring
 * - Plugin API integration
 */

// ============================================================
// GLOBAL STATE
// ============================================================

const SovereignApp = {
    sidebarOpen: true,
    notificationsOpen: false,
    userMenuOpen: false,
    currentPage: 'dashboard',
    coreStatus: 'active',
    notifications: [],
    currentTenantId: null, // Store current tenant
};

// ============================================================
// SIDEBAR MANAGEMENT
// ============================================================

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    SovereignApp.sidebarOpen = !SovereignApp.sidebarOpen;
    
    if (SovereignApp.sidebarOpen) {
        sidebar.classList.remove('-translate-x-full');
    } else {
        sidebar.classList.add('-translate-x-full');
    }
}

// Close sidebar on mobile when clicking outside
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    
    if (window.innerWidth < 1024 && 
        SovereignApp.sidebarOpen && 
        !sidebar.contains(event.target) && 
        !sidebarToggle.contains(event.target)) {
        toggleSidebar();
    }
});

// ============================================================
// NAVIGATION & BREADCRUMB
// ============================================================

function updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('breadcrumb');
    
    // Parse path to generate breadcrumb
    const segments = path.split('/').filter(s => s);
    
    let breadcrumbHTML = '';
    if (segments.length === 0) {
        breadcrumbHTML = '<span class="font-medium text-[var(--text-main)]">Dashboard</span>';
    } else {
        breadcrumbHTML = '<a href="/" class="hover:text-[var(--text-main)]">Dashboard</a>';
        
        segments.forEach((segment, index) => {
            const isLast = index === segments.length - 1;
            const formattedSegment = segment
                .split('-')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            
            if (isLast) {
                breadcrumbHTML += ` <span class="mx-2">/</span> <span class="font-medium text-[var(--text-main)]">${formattedSegment}</span>`;
            } else {
                breadcrumbHTML += ` <span class="mx-2">/</span> <a href="/${segments.slice(0, index + 1).join('/')}" class="hover:text-[var(--text-main)]">${formattedSegment}</a>`;
            }
        });
    }
    
    breadcrumb.innerHTML = breadcrumbHTML;
}

// Update active nav link
function updateActiveNavLink(path) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('bg-[var(--bg-selected)]', 'text-[var(--accent)]');
        
        if (link.getAttribute('href') === path) {
            link.classList.add('bg-[var(--bg-selected)]', 'text-[var(--accent)]');
        }
    });
}

// ============================================================
// NOTIFICATIONS
// ============================================================

function showNotification(message, type = 'info', duration = 5000) {
    const notification = {
        id: Date.now(),
        message,
        type, // info, success, warning, error
        timestamp: new Date()
    };
    
    SovereignApp.notifications.push(notification);
    renderNotification(notification);
    
    // Auto-dismiss
    if (duration > 0) {
        setTimeout(() => {
            dismissNotification(notification.id);
        }, duration);
    }
    
    // Update badge
    updateNotificationBadge();
}

function renderNotification(notification) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-[var(--z-tooltip)] space-y-2';
        document.body.appendChild(container);
    }
    
    // Color mapping
    const colors = {
        info: { bg: 'var(--info-light)', border: 'var(--info)', text: 'var(--info-dark)' },
        success: { bg: 'var(--success-light)', border: 'var(--success)', text: 'var(--success-dark)' },
        warning: { bg: 'var(--warning-light)', border: 'var(--warning)', text: 'var(--warning-dark)' },
        error: { bg: 'var(--error-light)', border: 'var(--error)', text: 'var(--error-dark)' }
    };
    
    const color = colors[notification.type] || colors.info;
    
    // Create notification element
    const div = document.createElement('div');
    div.id = `notification-${notification.id}`;
    div.className = 'max-w-sm w-full rounded-lg shadow-lg border-l-4 p-4 fade-in';
    div.style.backgroundColor = color.bg;
    div.style.borderColor = color.border;
    
    div.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                ${getNotificationIcon(notification.type)}
            </div>
            <div class="ml-3 flex-1">
                <p class="text-sm font-medium" style="color: ${color.text}">
                    ${notification.message}
                </p>
            </div>
            <div class="ml-4 flex-shrink-0">
                <button onclick="dismissNotification(${notification.id})" class="inline-flex rounded-md focus:outline-none">
                    <svg class="h-5 w-5" style="color: ${color.text}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(div);
}

function getNotificationIcon(type) {
    const icons = {
        info: '<svg class="h-5 w-5" style="color: var(--info)" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        success: '<svg class="h-5 w-5" style="color: var(--success)" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        warning: '<svg class="h-5 w-5" style="color: var(--warning)" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
        error: '<svg class="h-5 w-5" style="color: var(--error)" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
    };
    
    return icons[type] || icons.info;
}

function dismissNotification(id) {
    const element = document.getElementById(`notification-${id}`);
    if (element) {
        element.style.opacity = '0';
        setTimeout(() => {
            element.remove();
        }, 300);
    }
    
    SovereignApp.notifications = SovereignApp.notifications.filter(n => n.id !== id);
    updateNotificationBadge();
}

function updateNotificationBadge() {
    const badge = document.getElementById('notification-badge');
    if (badge) {
        if (SovereignApp.notifications.length > 0) {
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    }
}

function toggleNotifications() {
    SovereignApp.notificationsOpen = !SovereignApp.notificationsOpen;
    
    if (SovereignApp.notificationsOpen) {
        showNotificationsPanel();
    } else {
        hideNotificationsPanel();
    }
}

function showNotificationsPanel() {
    // Implementation for notifications panel
    // This would show a dropdown with notification history
    console.log('Show notifications panel');
}

function hideNotificationsPanel() {
    console.log('Hide notifications panel');
}

// ============================================================
// MODALS
// ============================================================

function showModal(title, content, actions = []) {
    // Create modal backdrop
    const backdrop = document.createElement('div');
    backdrop.id = 'modal-backdrop';
    backdrop.className = 'fixed inset-0 z-[var(--z-modal-backdrop)] flex items-center justify-center';
    backdrop.style.backgroundColor = 'var(--bg-modal)';
    backdrop.onclick = (e) => {
        if (e.target === backdrop) {
            closeModal();
        }
    };
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'bg-white rounded-lg shadow-xl max-w-md w-full mx-4 fade-in';
    
    // Build actions HTML
    let actionsHTML = '';
    if (actions.length > 0) {
        actionsHTML = '<div class="px-6 py-4 border-t border-[var(--border-color)] flex justify-end space-x-3">';
        actions.forEach(action => {
            const btnClass = action.primary 
                ? 'px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90'
                : 'px-4 py-2 bg-white border border-[var(--border-color)] text-[var(--text-main)] rounded-lg hover:bg-[var(--bg-hover)]';
            
            actionsHTML += `<button onclick="${action.onclick}" class="${btnClass}">${action.label}</button>`;
        });
        actionsHTML += '</div>';
    }
    
    modal.innerHTML = `
        <div class="px-6 py-4 border-b border-[var(--border-color)]">
            <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-[var(--text-main)]">${title}</h3>
                <button onclick="closeModal()" class="text-[var(--text-secondary)] hover:text-[var(--text-main)]">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        </div>
        <div class="px-6 py-4">
            ${content}
        </div>
        ${actionsHTML}
    `;
    
    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);
}

function closeModal() {
    const backdrop = document.getElementById('modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

// ============================================================
// USER MENU
// ============================================================

function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    SovereignApp.userMenuOpen = !SovereignApp.userMenuOpen;
    
    if (SovereignApp.userMenuOpen) {
        menu.classList.remove('hidden');
    } else {
        menu.classList.add('hidden');
    }
}

// Close user menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.getElementById('user-menu');
    const button = event.target.closest('button');
    
    if (SovereignApp.userMenuOpen && 
        !menu.contains(event.target) && 
        (!button || !button.onclick || button.onclick.toString().indexOf('toggleUserMenu') === -1)) {
        toggleUserMenu();
    }
});

// ============================================================
// CORE STATUS MONITORING
// ============================================================

async function checkCoreStatus() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        updateCoreStatus(data.status);
    } catch (error) {
        console.error('Core status check failed:', error);
        updateCoreStatus('error');
    }
}

function updateCoreStatus(status) {
    SovereignApp.coreStatus = status;
    
    const indicator = document.querySelector('.bg-\\[var\\(--success-light\\)\\]');
    if (!indicator) return;
    
    const statusColors = {
        active: { bg: 'var(--success-light)', dot: 'var(--success)', text: 'var(--success-dark)', label: 'Core Active' },
        degraded: { bg: 'var(--warning-light)', dot: 'var(--warning)', text: 'var(--warning-dark)', label: 'Core Degraded' },
        error: { bg: 'var(--error-light)', dot: 'var(--error)', text: 'var(--error-dark)', label: 'Core Error' }
    };
    
    const colors = statusColors[status] || statusColors.error;
    
    indicator.style.backgroundColor = colors.bg;
    const dot = indicator.querySelector('.animate-pulse');
    if (dot) dot.style.backgroundColor = colors.dot;
    const text = indicator.querySelector('span');
    if (text) {
        text.textContent = colors.label;
        text.style.color = colors.text;
    }
}

// Check core status every 30 seconds
setInterval(checkCoreStatus, 30000);
checkCoreStatus(); // Initial check

// ============================================================
// LOADING STATES
// ============================================================

function showLoading(target = '#main-content') {
    const element = document.querySelector(target);
    if (element) {
        element.innerHTML = `
            <div class="flex items-center justify-center h-64">
                <div class="text-center">
                    <svg class="animate-spin h-12 w-12 mx-auto mb-4" style="color: var(--accent)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p class="text-[var(--text-secondary)]">Loading...</p>
                </div>
            </div>
        `;
    }
}

function hideLoading() {
    // Loading is replaced by HTMX content automatically
}

// ============================================================
// FORM HELPERS
// ============================================================

function serializeForm(formElement) {
    const formData = new FormData(formElement);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-[var(--error)]');
        } else {
            input.classList.remove('border-[var(--error)]');
        }
    });
    
    return isValid;
}

// ============================================================
// TENANT MANAGEMENT (NEW)
// ============================================================

/**
 * Get current tenant ID from URL
 * Supports patterns like:
 * - /tenants/acme_corp/dashboard
 * - /dashboard (uses default tenant from localStorage)
 */
function getTenantId() {
    // 1. Check in-memory state first (fastest)
    if (SovereignApp.currentTenantId) {
        return SovereignApp.currentTenantId;
    }

    // 2. Read from sessionStorage — this is where auth.js stores the tenant_id
    //    after the magic link callback. Always check here before falling back.
    const sessionTenant = sessionStorage.getItem('dodman_tenant_id');
    if (sessionTenant) {
        SovereignApp.currentTenantId = sessionTenant;
        return sessionTenant;
    }

    // 3. Try to decode it from the session token if tenant_id key is missing
    const sessionToken = sessionStorage.getItem('dodman_session_token');
    if (sessionToken) {
        try {
            const base64 = sessionToken.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(atob(base64));
            if (payload.tenant_id) {
                SovereignApp.currentTenantId = payload.tenant_id;
                sessionStorage.setItem('dodman_tenant_id', payload.tenant_id);
                return payload.tenant_id;
            }
        } catch (e) { /* ignore decode errors */ }
    }

    // 4. Try to get from URL path (e.g. /tenants/acme_corp/dashboard)
    const pathParts = window.location.pathname.split('/').filter(p => p);
    const tenantIndex = pathParts.indexOf('tenants');
    if (tenantIndex !== -1 && pathParts[tenantIndex + 1]) {
        const tenantId = pathParts[tenantIndex + 1];
        SovereignApp.currentTenantId = tenantId;
        return tenantId;
    }

    // 5. Last resort — localStorage (legacy fallback)
    const storedTenant = loadFromLocalStorage('current_tenant_id');
    if (storedTenant) {
        SovereignApp.currentTenantId = storedTenant;
        return storedTenant;
    }

    console.warn('No tenant ID found — auth.js may not have run yet');
    return null;
}

/**
 * Set current tenant ID
 */
function setTenantId(tenantId) {
    SovereignApp.currentTenantId = tenantId;
    saveToLocalStorage('current_tenant_id', tenantId);
}

// ============================================================
// AUTHENTICATION (NEW)
// ============================================================

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
    // auth.js stores the token in sessionStorage under 'dodman_session_token'
    return sessionStorage.getItem('dodman_session_token')
        || loadFromLocalStorage('auth_token')  // legacy fallback
        || '';
}

/**
 * Set authentication token
 */
function setAuthToken(token) {
    // Store in sessionStorage to stay consistent with auth.js
    sessionStorage.setItem('dodman_session_token', token);
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    const token = getAuthToken();
    if (!token) return false;
    // Also verify token is not expired
    try {
        const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(atob(base64));
        return payload.exp ? (payload.exp * 1000) > Date.now() : true;
    } catch {
        return token.length > 0;
    }
}

/**
 * Logout user
 */
function logout() {
    // Delegate to AUTH.logout() from auth.js which calls the dodman-core
    // logout API and redirects to ai.dodman.group/login.html.
    // If auth.js hasn't loaded yet, fall back to a direct redirect.
    if (window.AUTH && typeof window.AUTH.logout === 'function') {
        window.AUTH.logout();
    } else {
        sessionStorage.clear();
        localStorage.removeItem('auth_token');
        localStorage.removeItem('current_tenant_id');
        window.location.href = 'https://ai.dodman.group/login.html';
    }
}

// ============================================================
// API HELPERS (ENHANCED FOR PLUGINS)
// ============================================================

/**
 * Make API request with automatic auth header injection
 * Enhanced to support plugin API routes
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // Add auth token if available
    const token = getAuthToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        
        // Handle 401 unauthorized
        if (response.status === 401) {
            showNotification('Session expired. Please login again.', 'error');
            setTimeout(() => logout(), 2000); // delegates to AUTH.logout()
            throw new Error('Unauthorized');
        }
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || result.message || 'API request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// ============================================================
// CLIPBOARD
// ============================================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
        showNotification('Failed to copy', 'error');
    });
}

// ============================================================
// LOCAL STORAGE HELPERS
// ============================================================

function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('LocalStorage save failed:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('LocalStorage load failed:', error);
        return defaultValue;
    }
}

/**
 * Get data from localStorage (alias for backward compatibility)
 */
function getFromLocalStorage(key, defaultValue = null) {
    return loadFromLocalStorage(key, defaultValue);
}

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sovereign Dashboard initialized');
    
    // Initialize tenant context from sessionStorage (set by auth.js)
    const tenantId = getTenantId();
    if (tenantId) {
        SovereignApp.currentTenantId = tenantId;
        console.log('Current tenant:', tenantId);
    } else {
        console.warn('Tenant ID not yet available — auth.js may still be initialising');
    }
    
    // Update initial breadcrumb
    updateBreadcrumb(window.location.pathname);
    
    // Update active nav link
    updateActiveNavLink(window.location.pathname);
    
    // Only show welcome if authenticated
    if (isAuthenticated()) {
        showNotification('Welcome to Sovereign!', 'success', 3000);
    }
});

// ============================================================
// EXPORT FOR GLOBAL ACCESS
// ============================================================

window.Sovereign = {
    // State
    app: SovereignApp,
    
    // UI Functions
    showNotification,
    dismissNotification,
    showModal,
    closeModal,
    showLoading,
    hideLoading,
    
    // Navigation
    updateBreadcrumb,
    updateActiveNavLink,
    
    // Forms
    serializeForm,
    validateForm,
    
    // Tenant Management
    getTenantId,
    setTenantId,
    
    // Authentication
    getAuthToken,
    setAuthToken,
    isAuthenticated,
    logout,
    
    // API
    apiRequest,
    
    // Utilities
    copyToClipboard,
    saveToLocalStorage,
    loadFromLocalStorage,
    getFromLocalStorage, 
};

console.log('Sovereign global utilities loaded');