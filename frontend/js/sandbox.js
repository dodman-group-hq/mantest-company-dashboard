/**
 * Sovereign Plugin Sandbox - JavaScript
 * 
 * Development environment for testing plugins in isolation with:
 * - Context simulation (Founder vs Tenant)
 * - Mock vault storage
 * - Theme customization
 * - Console logging
 */

// ============================================================
// SANDBOX STATE
// ============================================================

const SandboxState = {
    currentPlugin: null,
    contextMode: 'founder', // 'founder' or 'tenant'
    tenantId: null,
    mockVault: {
        collections: {}
    },
    themeColors: {
        primary: '#1a1a1a',
        secondary: '#f4f4f4',
        accent: '#3b82f6'
    },
    consoleHistory: []
};

// ============================================================
// PLUGIN MANAGEMENT
// ============================================================

function loadPlugin(pluginName) {
    if (!pluginName) return;
    
    SandboxState.currentPlugin = pluginName;
    logToConsole(`Selected plugin: ${pluginName}`, 'info');
}

function loadSelectedPlugin() {
    const select = document.getElementById('plugin-selector');
    const pluginName = select.value;
    
    if (!pluginName) {
        alert('Please select a plugin first');
        return;
    }
    
    logToConsole(`Loading plugin: ${pluginName}...`, 'info');
    
    // Update status
    document.getElementById('plugin-status').textContent = `Loading ${pluginName}...`;
    
    // Simulate plugin loading with HTMX
    const url = `/api/sandbox/plugins/${pluginName}?mode=${SandboxState.contextMode}&tenant_id=${SandboxState.tenantId || ''}`;
    
    // Show loading state
    document.getElementById('plugin-content').innerHTML = `
        <div class="flex items-center justify-center h-full">
            <div class="text-center">
                <svg class="animate-spin h-12 w-12 mx-auto mb-4" style="color: var(--accent)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="text-[var(--text-secondary)]">Loading ${pluginName}...</p>
            </div>
        </div>
    `;
    
    // Simulate API call (in production, this would use HTMX)
    setTimeout(() => {
        loadMockPluginContent(pluginName);
        logToConsole(`Plugin ${pluginName} loaded successfully`, 'success');
        document.getElementById('plugin-status').textContent = `${pluginName} (${SandboxState.contextMode} mode)`;
    }, 1000);
}

function loadMockPluginContent(pluginName) {
    const content = document.getElementById('plugin-content');
    
    // Mock plugin content based on plugin name
    if (pluginName === 'sniper') {
        content.innerHTML = `
            <div class="space-y-6">
                <div>
                    <h3 class="text-2xl font-bold text-[var(--text-main)] mb-2">
                        🎯 Sniper Plugin
                    </h3>
                    <p class="text-[var(--text-secondary)]">
                        Lead hunting in ${SandboxState.contextMode} mode
                    </p>
                </div>
                
                <!-- Stats -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="p-4 bg-[var(--bg-hover)] rounded-lg">
                        <p class="text-sm text-[var(--text-secondary)] mb-1">Leads Found</p>
                        <p class="text-2xl font-bold text-[var(--text-main)]">23</p>
                    </div>
                    <div class="p-4 bg-[var(--bg-hover)] rounded-lg">
                        <p class="text-sm text-[var(--text-secondary)] mb-1">Avg Score</p>
                        <p class="text-2xl font-bold text-[var(--text-main)]">87.5</p>
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="space-y-3">
                    <button onclick="runScour()" class="w-full px-4 py-3 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition-opacity">
                        Run Scour
                    </button>
                    <button onclick="viewLeads()" class="w-full px-4 py-3 border border-[var(--border-color)] text-[var(--text-main)] rounded-lg hover:bg-[var(--bg-hover)] transition-colors">
                        View Leads
                    </button>
                </div>
                
                <!-- Mock Lead List -->
                <div class="border border-[var(--border-color)] rounded-lg overflow-hidden">
                    <div class="px-4 py-3 bg-[var(--bg-side)] border-b border-[var(--border-color)]">
                        <h4 class="font-semibold text-[var(--text-main)]">Recent Leads</h4>
                    </div>
                    <div class="divide-y divide-[var(--border-color)]">
                        <div class="p-4 hover:bg-[var(--bg-hover)] cursor-pointer">
                            <div class="flex items-center justify-between mb-2">
                                <p class="font-medium text-[var(--text-main)]">Acme Corp</p>
                                <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">92</span>
                            </div>
                            <p class="text-sm text-[var(--text-secondary)]">Just raised $10M Series A</p>
                        </div>
                        <div class="p-4 hover:bg-[var(--bg-hover)] cursor-pointer">
                            <div class="flex items-center justify-between mb-2">
                                <p class="font-medium text-[var(--text-main)]">TechStart Inc</p>
                                <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">85</span>
                            </div>
                            <p class="text-sm text-[var(--text-secondary)]">Hiring 5 SDRs</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else if (pluginName === 'shadow') {
        content.innerHTML = `
            <div class="space-y-6">
                <div>
                    <h3 class="text-2xl font-bold text-[var(--text-main)] mb-2">
                        🕵️ Shadow Plugin
                    </h3>
                    <p class="text-[var(--text-secondary)]">
                        Intelligence gathering in ${SandboxState.contextMode} mode
                    </p>
                </div>
                
                <!-- Intelligence Stats -->
                <div class="grid grid-cols-3 gap-4">
                    <div class="p-4 bg-[var(--bg-hover)] rounded-lg text-center">
                        <p class="text-sm text-[var(--text-secondary)] mb-1">Rivals</p>
                        <p class="text-2xl font-bold text-[var(--text-main)]">12</p>
                    </div>
                    <div class="p-4 bg-[var(--bg-hover)] rounded-lg text-center">
                        <p class="text-sm text-[var(--text-secondary)] mb-1">Intel</p>
                        <p class="text-2xl font-bold text-[var(--text-main)]">47</p>
                    </div>
                    <div class="p-4 bg-[var(--bg-hover)] rounded-lg text-center">
                        <p class="text-sm text-[var(--text-secondary)] mb-1">Signals</p>
                        <p class="text-2xl font-bold text-[var(--text-main)]">8</p>
                    </div>
                </div>
                
                <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p class="text-sm text-blue-900">
                        🔍 This is a mock Shadow plugin interface. In production, this would show real competitive intelligence.
                    </p>
                </div>
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="text-center py-12">
                <svg class="w-16 h-16 mx-auto mb-4 text-[var(--text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
                <h3 class="text-lg font-medium text-[var(--text-main)] mb-2">
                    Custom Plugin: ${pluginName}
                </h3>
                <p class="text-sm text-[var(--text-secondary)]">
                    Plugin interface would render here
                </p>
            </div>
        `;
    }
    
    // Initialize any plugin-specific JS
    initializePluginInteractions();
}

function initializePluginInteractions() {
    // Add any plugin-specific event listeners or initialization
    logToConsole('Plugin interactions initialized', 'info');
}

// ============================================================
// CONTEXT MANAGEMENT
// ============================================================

function setContextMode(mode) {
    SandboxState.contextMode = mode;
    
    // Update UI
    const founderBtn = document.getElementById('mode-founder');
    const tenantBtn = document.getElementById('mode-tenant');
    const tenantField = document.getElementById('tenant-id-field');
    const contextDisplay = document.getElementById('context-display');
    
    if (mode === 'founder') {
        founderBtn.classList.add('bg-[var(--accent)]', 'text-white');
        founderBtn.classList.remove('bg-white', 'text-[var(--text-main)]');
        tenantBtn.classList.remove('bg-[var(--accent)]', 'text-white');
        tenantBtn.classList.add('bg-white', 'text-[var(--text-main)]');
        
        tenantField.classList.add('hidden');
        SandboxState.tenantId = null;
        
        contextDisplay.textContent = 'Founder Mode (God Mode)';
        
        logToConsole('Switched to Founder Mode', 'info');
    } else {
        tenantBtn.classList.add('bg-[var(--accent)]', 'text-white');
        tenantBtn.classList.remove('bg-white', 'text-[var(--text-main)]');
        founderBtn.classList.remove('bg-[var(--accent)]', 'text-white');
        founderBtn.classList.add('bg-white', 'text-[var(--text-main)]');
        
        tenantField.classList.remove('hidden');
        SandboxState.tenantId = document.getElementById('tenant-id').value;
        
        contextDisplay.textContent = `Tenant Mode: ${SandboxState.tenantId}`;
        
        logToConsole(`Switched to Tenant Mode: ${SandboxState.tenantId}`, 'info');
    }
    
    // Reload plugin if one is loaded
    if (SandboxState.currentPlugin) {
        loadMockPluginContent(SandboxState.currentPlugin);
    }
}

// Update tenant ID when input changes
document.addEventListener('DOMContentLoaded', function() {
    const tenantInput = document.getElementById('tenant-id');
    if (tenantInput) {
        tenantInput.addEventListener('change', function() {
            SandboxState.tenantId = this.value;
            document.getElementById('context-display').textContent = `Tenant Mode: ${SandboxState.tenantId}`;
            logToConsole(`Tenant ID updated: ${SandboxState.tenantId}`, 'info');
        });
    }
});

// ============================================================
// THEME CUSTOMIZATION (MIRROR PREVIEW)
// ============================================================

function updateThemeColor(colorName, hexValue) {
    SandboxState.themeColors[colorName] = hexValue;
    
    // Update CSS variable
    document.documentElement.style.setProperty(`--${colorName}`, hexValue);
    
    // Update hex input
    document.getElementById(`${colorName}-color-hex`).value = hexValue;
    
    logToConsole(`Updated ${colorName} color: ${hexValue}`, 'info');
}

function updateThemeColorFromHex(colorName, hexValue) {
    // Validate hex
    if (!/^#[0-9A-F]{6}$/i.test(hexValue)) {
        logToConsole(`Invalid hex color: ${hexValue}`, 'error');
        return;
    }
    
    SandboxState.themeColors[colorName] = hexValue;
    
    // Update CSS variable
    document.documentElement.style.setProperty(`--${colorName}`, hexValue);
    
    // Update color picker
    document.getElementById(`${colorName}-color`).value = hexValue;
    
    logToConsole(`Updated ${colorName} color: ${hexValue}`, 'info');
}

function resetThemeColors() {
    const defaults = {
        primary: '#1a1a1a',
        secondary: '#f4f4f4',
        accent: '#3b82f6'
    };
    
    Object.keys(defaults).forEach(colorName => {
        updateThemeColor(colorName, defaults[colorName]);
        document.getElementById(`${colorName}-color`).value = defaults[colorName];
    });
    
    logToConsole('Theme colors reset to defaults', 'info');
}

function applyPreset(presetName) {
    const presets = {
        tech: {
            primary: '#0ea5e9',
            secondary: '#f0f9ff',
            accent: '#3b82f6'
        },
        finance: {
            primary: '#059669',
            secondary: '#ecfdf5',
            accent: '#10b981'
        },
        creative: {
            primary: '#a855f7',
            secondary: '#faf5ff',
            accent: '#c026d3'
        }
    };
    
    const preset = presets[presetName];
    if (!preset) {
        logToConsole(`Unknown preset: ${presetName}`, 'error');
        return;
    }
    
    Object.keys(preset).forEach(colorName => {
        updateThemeColor(colorName, preset[colorName]);
        document.getElementById(`${colorName}-color`).value = preset[colorName];
    });
    
    logToConsole(`Applied ${presetName} preset`, 'success');
}

// ============================================================
// MOCK VAULT
// ============================================================

function updateVaultDisplay() {
    const vaultData = document.getElementById('vault-data');
    vaultData.textContent = JSON.stringify(SandboxState.mockVault, null, 2);
}

function refreshVault() {
    logToConsole('Refreshing vault...', 'info');
    
    // Simulate fetching vault data
    setTimeout(() => {
        updateVaultDisplay();
        logToConsole('Vault refreshed', 'success');
    }, 500);
}

function clearVault() {
    if (confirm('Are you sure you want to clear the mock vault?')) {
        SandboxState.mockVault = {
            collections: {}
        };
        updateVaultDisplay();
        logToConsole('Vault cleared', 'warning');
    }
}

function exportVault() {
    const dataStr = JSON.stringify(SandboxState.mockVault, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `vault-export-${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    logToConsole('Vault exported', 'success');
}

function importVault() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                SandboxState.mockVault = data;
                updateVaultDisplay();
                logToConsole('Vault imported successfully', 'success');
            } catch (error) {
                logToConsole('Failed to import vault: Invalid JSON', 'error');
            }
        };
        
        reader.readAsText(file);
    };
    
    input.click();
}

// ============================================================
// PLUGIN ACTIONS
// ============================================================

function triggerPluginAction(action) {
    logToConsole(`Triggering plugin action: ${action}`, 'info');
    
    // Simulate plugin action
    switch (action) {
        case 'scour':
            simulateScour();
            break;
        case 'prospect':
            simulateAddProspect();
            break;
        case 'complete':
            simulateCompletion();
            break;
        default:
            logToConsole(`Unknown action: ${action}`, 'error');
    }
}

function simulateScour() {
    logToConsole('Running scour...', 'info');
    
    // Add mock data to vault
    const mockLeads = [
        { name: 'Acme Corp', score: 92, source: 'twitter' },
        { name: 'TechStart Inc', score: 85, source: 'apollo' }
    ];
    
    if (!SandboxState.mockVault.collections['sniper_leads']) {
        SandboxState.mockVault.collections['sniper_leads'] = [];
    }
    
    SandboxState.mockVault.collections['sniper_leads'].push({
        timestamp: new Date().toISOString(),
        mode: SandboxState.contextMode,
        leads: mockLeads
    });
    
    updateVaultDisplay();
    
    setTimeout(() => {
        logToConsole(`Scour complete: Found ${mockLeads.length} leads`, 'success');
    }, 2000);
}

function simulateAddProspect() {
    logToConsole('Adding mock prospect...', 'info');
    
    const prospect = {
        id: 'prospect_' + Date.now(),
        name: 'Mock Company',
        domain: 'mockcompany.com',
        added_at: new Date().toISOString()
    };
    
    if (!SandboxState.mockVault.collections['prospects']) {
        SandboxState.mockVault.collections['prospects'] = [];
    }
    
    SandboxState.mockVault.collections['prospects'].push(prospect);
    updateVaultDisplay();
    
    logToConsole(`Prospect added: ${prospect.name}`, 'success');
}

function simulateCompletion() {
    logToConsole('Simulating plugin completion...', 'info');
    
    setTimeout(() => {
        logToConsole('Plugin completed successfully', 'success');
        
        // Show mock notification
        showSandboxNotification('Plugin task completed!', 'success');
    }, 1500);
}

// Mock plugin-specific actions
function runScour() {
    simulateScour();
}

function viewLeads() {
    logToConsole('Viewing leads...', 'info');
    showSandboxNotification('Lead view would open here', 'info');
}

// ============================================================
// CONSOLE
// ============================================================

function logToConsole(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const entry = {
        timestamp,
        message,
        type
    };
    
    SandboxState.consoleHistory.push(entry);
    
    const console = document.getElementById('console-output');
    
    const colors = {
        info: 'text-blue-400',
        success: 'text-green-400',
        warning: 'text-yellow-400',
        error: 'text-red-400'
    };
    
    const colorClass = colors[type] || colors.info;
    
    const line = document.createElement('p');
    line.className = colorClass;
    line.textContent = `[${timestamp}] ${message}`;
    
    console.appendChild(line);
    console.scrollTop = console.scrollHeight;
}

function clearConsole() {
    SandboxState.consoleHistory = [];
    document.getElementById('console-output').innerHTML = '';
    logToConsole('Console cleared', 'info');
}

// ============================================================
// NOTIFICATIONS
// ============================================================

function showSandboxNotification(message, type = 'info') {
    // Reuse global notification system if available
    if (window.Sovereign && window.Sovereign.showNotification) {
        window.Sovereign.showNotification(message, type);
    } else {
        alert(message);
    }
}

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    logToConsole('Sandbox initialized', 'success');
    logToConsole('Ready for plugin testing', 'info');
    
    // Initialize vault display
    updateVaultDisplay();
    
    // Set default context mode
    setContextMode('founder');
});

// ============================================================
// EXPORT
// ============================================================

window.Sandbox = {
    state: SandboxState,
    loadPlugin,
    loadSelectedPlugin,
    setContextMode,
    updateThemeColor,
    resetThemeColors,
    applyPreset,
    refreshVault,
    clearVault,
    exportVault,
    importVault,
    triggerPluginAction,
    logToConsole,
    clearConsole
};

console.log('Sandbox utilities loaded');