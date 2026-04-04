# Sovereign Master Template

**High-Performance, Framework-Less Dashboard Template for Dodman Core V2**

> The universal frame for all Sovereign private repos with built-in Plugin Sandbox

---

## 🎯 Overview

The Sovereign Master Template is a production-ready, framework-free dashboard template built with:
- **Vanilla JavaScript** - No framework dependencies
- **HTMX** - Dynamic content loading without full page refreshes
- **Tailwind CSS** - Utility-first styling
- **Mirror Theme Engine** - Dynamic brand theming via CSS variables

---

## 🏗️ Architecture

### **The "DNA" of Sovereign**

```
sovereign-template/
├── index.html              # Master frame with sidebar & HTMX integration
├── admin/
│   └── sandbox.html        # Plugin sandbox (dev only)
├── css/
│   └── theme.css          # Mirror theme engine with CSS variables
├── js/
│   ├── global.js          # Shared UI logic (notifications, modals, etc.)
│   └── sandbox.js         # Sandbox functionality
└── assets/
    ├── logo.svg           # Replaced during mirroring
    └── favicon.png        # Replaced during mirroring
```

---

## ✨ Key Features

### **1. Mirror Theme Engine**

Dynamic brand theming without hardcoded colors:

```css
:root {
  --primary: #1a1a1a;      /* Client's primary brand color */
  --secondary: #f4f4f4;    /* Client's secondary color */
  --accent: #3b82f6;       /* Highlight/CTA color */
  /* ... 50+ theme variables */
}
```

**How it works:**
1. Dodman Core fetches client's brand colors
2. Core injects new CSS variables
3. Entire UI updates automatically - no rebuild required

### **2. Master Frame Layout**

Responsive, SaaS-style layout with:
- **Collapsible sidebar** with navigation
- **Top bar** with status indicators and user menu
- **Main content area** (HTMX target)
- **Mobile-responsive** design

### **3. Plugin Sandbox**

Development environment (`/admin/sandbox`) with:
- **Plugin selector** - Load any plugin for testing
- **Context toggler** - Simulate Founder vs Tenant mode
- **Mock vault** - View simulated plugin data storage
- **Mirror preview** - Test theme with different brand colors
- **Console output** - Real-time logging

### **4. HTMX Integration**

Zero-JavaScript plugin loading:

```html
<a hx-get="/api/plugins/sniper/dashboard" 
   hx-target="#main-content" 
   hx-push-url="true">
    Lead Sniper
</a>
```

**Benefits:**
- No page reloads
- SEO-friendly URLs
- Progressive enhancement
- Automatic loading states

---

## 🚀 Quick Start

### **1. Clone Template**

```bash
git clone https://github.com/dodman-group/sovereign-template.git my-client-dashboard
cd my-client-dashboard
```

### **2. Configure Environment**

Create `.env` file:

```env
# Client Configuration
TENANT_ID=acme_corp
CLIENT_NAME=Acme Corporation
CLIENT_DOMAIN=acme.com

# Branding (fetched from Core, but can override)
PRIMARY_COLOR=#1a1a1a
SECONDARY_COLOR=#f4f4f4
ACCENT_COLOR=#3b82f6

# API
DODMAN_CORE_URL=https://api.dodman.ai
API_KEY=your_api_key_here

# Environment
NODE_ENV=production
ENABLE_SANDBOX=false  # Only true in development
```

### **3. Install Dependencies** (Optional)

```bash
# If using build tools
npm install

# Or just serve static files
python -m http.server 8000
```

### **4. Deploy**

```bash
# Copy files to web server
rsync -av --exclude node_modules ./ user@server:/var/www/acme-dashboard/

# Or use deployment script
./deploy.sh production
```

---

## 🎨 Theme Customization

### **Automatic (via Dodman Core)**

Core automatically fetches and applies client branding:

```javascript
// Core injects theme during mirroring
fetch('/api/mirror/generate', {
    method: 'POST',
    body: JSON.stringify({
        tenant_id: 'acme_corp',
        branding: {
            logo_url: 'https://acme.com/logo.svg',
            primary_color: '#FF5733',
            secondary_color: '#33FF57'
        }
    })
});
```

### **Manual Override**

Edit `theme.css` directly:

```css
:root {
  --primary: #YOUR_COLOR;
  --secondary: #YOUR_COLOR;
  --accent: #YOUR_COLOR;
}
```

### **Runtime Customization** (Sandbox)

Use color pickers in `/admin/sandbox` to test themes live.

---

## 🔌 Plugin Integration

### **Adding a Plugin**

1. **Add Navigation Link** in `index.html`:

```html
<a href="/plugins/my-plugin" 
   hx-get="/api/plugins/my-plugin/dashboard" 
   hx-target="#main-content" 
   hx-push-url="true"
   class="nav-link">
    My Plugin
</a>
```

2. **Create Plugin Endpoint** (Backend):

```python
@app.get("/api/plugins/my-plugin/dashboard")
def my_plugin_dashboard():
    return render_template('plugins/my-plugin.html')
```

3. **Plugin HTML Template**:

```html
<!-- plugins/my-plugin.html -->
<div class="space-y-6">
    <h2 class="text-2xl font-bold text-[var(--text-main)]">
        My Plugin
    </h2>
    
    <div class="bg-white rounded-lg p-6">
        <!-- Plugin content here -->
    </div>
</div>

<!-- Optional: Plugin-specific JavaScript -->
<script>
    // This runs when plugin is loaded via HTMX
    console.log('My plugin loaded');
</script>
```

### **Plugin Best Practices**

✅ **DO:**
- Use CSS variables for colors: `var(--primary)`
- Keep JS minimal (HTMX handles most interactions)
- Return only the content fragment (no full HTML)
- Log events for debugging

❌ **DON'T:**
- Hardcode colors or fonts
- Include `<html>`, `<head>`, or `<body>` tags
- Use `document.write()`
- Override global styles

---

## 🧪 Plugin Sandbox

### **Accessing the Sandbox**

Available only in development mode:

```bash
# Set environment variable
export ENABLE_SANDBOX=true

# Access sandbox
http://localhost:8000/admin/sandbox.html
```

### **Sandbox Features**

#### **1. Plugin Selector**

Load any plugin for testing:
- Select from dropdown
- Click "Load Plugin"
- Plugin renders in center panel

#### **2. Context Toggler**

Simulate execution context:
- **Founder Mode** - God Mode (tenant_id = NULL)
- **Tenant Mode** - Client context (tenant_id = UUID)

#### **3. Mock Vault**

View simulated plugin storage:
- JSON display of vault data
- Export/import functionality
- Clear vault data

#### **4. Mirror Preview**

Test theme with brand colors:
- Color pickers for primary/secondary/accent
- Live preview of changes
- Brand presets (Tech, Finance, Creative)
- Reset to defaults

#### **5. Test Actions**

Trigger plugin events:
- Run Scour
- Add Mock Prospect
- Simulate Completion
- Clear Mock Vault

#### **6. Console Output**

Real-time logging:
- Info, success, warning, error messages
- Timestamped entries
- Scrollable history
- Clear button

---

## 🎯 HTMX Event Handling

### **Global Events**

Handle HTMX events in `global.js`:

```javascript
// After content loads
document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    console.log('Content loaded:', evt.detail.target);
    
    // Execute plugin-specific JS
    const scripts = evt.detail.target.querySelectorAll('script');
    scripts.forEach(script => {
        eval(script.textContent);
    });
    
    // Update breadcrumb
    updateBreadcrumb(evt.detail.pathInfo.requestPath);
});

// Handle errors
document.body.addEventListener('htmx:responseError', function(evt) {
    console.error('HTMX Error:', evt.detail);
    showNotification('Error loading content', 'error');
});
```

---

## 🔒 Security

### **Content Security Policy**

Defined in `index.html`:

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; 
               style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; 
               connect-src 'self' /api/*;">
```

### **API Authentication**

All API calls require authentication:

```javascript
fetch('/api/endpoint', {
    headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
    }
});
```

### **Sandbox Protection**

Sandbox is only accessible in development:

```python
@app.get("/admin/sandbox")
def sandbox():
    if os.getenv('NODE_ENV') == 'production':
        abort(404)  # Hide in production
    
    return render_template('sandbox.html')
```

---

## 📱 Responsive Design

### **Breakpoints**

```css
/* Mobile: < 640px */
/* Tablet: 640px - 1024px */
/* Desktop: > 1024px */
```

### **Mobile Features**

- Collapsible sidebar
- Touch-friendly buttons
- Optimized layouts
- Hamburger menu

---

## 🎨 UI Components

### **Notifications**

```javascript
window.Sovereign.showNotification('Message', 'success', 5000);
// Types: info, success, warning, error
```

### **Modals**

```javascript
window.Sovereign.showModal('Title', '<p>Content</p>', [
    { label: 'Cancel', onclick: 'closeModal()' },
    { label: 'Confirm', onclick: 'handleConfirm()', primary: true }
]);
```

### **Loading States**

```javascript
window.Sovereign.showLoading('#main-content');
// HTMX automatically replaces with content
```

---

## 🔧 Customization

### **Adding a New Page**

1. Create HTML template
2. Add route in backend
3. Add navigation link
4. Test in sandbox

### **Changing Colors**

```css
/* In theme.css */
:root {
  --primary: #NEW_COLOR;
}
```

### **Adding Fonts**

```html
<!-- In index.html -->
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT&display=swap" rel="stylesheet">
```

```css
/* In theme.css */
:root {
  --font-family: 'YOUR_FONT', sans-serif;
}
```

---

## 🚢 Deployment

### **The "Spin" Prep**

1. **Clone repo**
2. **Find/replace** `{{TENANT_ID}}` with actual tenant ID
3. **Update .env** file
4. **Deploy!**

### **Deployment Script**

```bash
#!/bin/bash
# deploy.sh

TENANT_ID=$1
ENVIRONMENT=${2:-production}

echo "Deploying Sovereign for: $TENANT_ID"

# Find/replace tenant ID
find . -type f -name "*.html" -o -name "*.js" | xargs sed -i "s/{{TENANT_ID}}/$TENANT_ID/g"

# Deploy based on environment
if [ "$ENVIRONMENT" == "production" ]; then
    rsync -av ./ user@server:/var/www/$TENANT_ID-dashboard/
else
    echo "Starting dev server..."
    python -m http.server 8000
fi
```

Usage:

```bash
./deploy.sh acme_corp production
```

---

## 📊 Performance

### **Metrics**

- **First Paint**: < 1s
- **Interactive**: < 2s
- **Bundle Size**: ~50KB (CSS + JS)
- **Lighthouse Score**: 95+

### **Optimizations**

- Minimal JavaScript (no frameworks)
- CSS variables (no Sass compilation)
- HTMX for efficient updates
- Lazy-loaded plugins

---

## 🐛 Troubleshooting

### **Plugin Not Loading**

1. Check HTMX endpoint in Network tab
2. Verify backend route exists
3. Check CORS headers
4. Test in sandbox first

### **Theme Not Updating**

1. Verify CSS variables in DevTools
2. Check CSP allows inline styles
3. Clear browser cache
4. Inspect `:root` in Elements panel

### **Sandbox Not Working**

1. Ensure `ENABLE_SANDBOX=true`
2. Check console for errors
3. Verify all JS files loaded
4. Test in incognito mode

---

## 📚 API Reference

### **Global JavaScript API**

```javascript
window.Sovereign = {
    // UI
    showNotification(message, type, duration),
    showModal(title, content, actions),
    closeModal(),
    showLoading(target),
    
    // Navigation
    updateBreadcrumb(path),
    updateActiveNavLink(path),
    
    // Forms
    serializeForm(formElement),
    validateForm(formElement),
    
    // API
    apiRequest(endpoint, method, data),
    
    // Utilities
    copyToClipboard(text),
    saveToLocalStorage(key, value),
    loadFromLocalStorage(key, defaultValue)
};
```

### **Sandbox API**

```javascript
window.Sandbox = {
    // Plugin Management
    loadPlugin(pluginName),
    loadSelectedPlugin(),
    
    // Context
    setContextMode(mode),
    
    // Theme
    updateThemeColor(colorName, hexValue),
    resetThemeColors(),
    applyPreset(presetName),
    
    // Vault
    refreshVault(),
    clearVault(),
    exportVault(),
    importVault(),
    
    // Testing
    triggerPluginAction(action),
    logToConsole(message, type),
    clearConsole()
};
```

---

## 🎓 Best Practices

### **Development Workflow**

1. **Start with Sandbox** - Test plugin in isolation
2. **Test Both Contexts** - Founder and Tenant modes
3. **Try Different Themes** - Use Mirror preview
4. **Check Console** - Monitor events and errors
5. **Validate Vault** - Ensure data structure is correct
6. **Deploy to Staging** - Test in real environment
7. **Go Live** - Deploy to production

### **Code Standards**

- Use CSS variables for all colors
- Follow HTMX patterns for interactions
- Keep JavaScript minimal
- Comment complex logic
- Use semantic HTML
- Follow accessibility guidelines

---

## 📄 License

Proprietary - Dodman Group

---

## 🤝 Support

- **Documentation**: See `/docs` directory
- **Issues**: Submit via GitHub Issues
- **Contact**: dev@dodman.ai

---

## 🎉 Credits

Built with ❤️ by the Dodman Group team

**Technologies:**
- HTMX - Dynamic interactions
- Tailwind CSS - Utility-first styling
- Vanilla JS - No framework overhead

---

**Sovereign Master Template - The Universal Frame for All Private Repos**