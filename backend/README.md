# Master Dashboard Template - Backend

FastAPI backend that serves the universal dashboard frontend and proxies requests to dodman-core API.

## 🎯 Architecture

```
master-dashboard-template/
├── frontend/              # Static dashboard UI
│   ├── index.html        # Main dashboard
│   ├── css/theme.css     # Styling
│   ├── js/global.js      # JavaScript
│   └── admin/sandbox.html # Plugin sandbox
│
└── backend/              # FastAPI server (THIS)
    ├── main.py           # Main app + proxy
    ├── routes/
    │   ├── auth.py       # Auth routes
    │   └── plugins.py    # Plugin routes
    └── templates/plugins/ # Plugin-specific templates
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
DODMAN_CORE_API_URL=http://localhost:8080  # Your dodman-core API
PORT=3000
ENVIRONMENT=development
```

### 3. Run Server

```bash
# Development (auto-reload)
python main.py

# Or with uvicorn
uvicorn main:app --reload --port 3000

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:3000
```

### 4. Access Dashboard

```
http://localhost:3000          # Main dashboard
http://localhost:3000/api/docs # API documentation
```

---

## 📡 How It Works

### **Proxy Architecture**

The backend acts as a **transparent proxy** to dodman-core API:

```
Frontend Request:
POST /api/auth/login
  ↓
Backend Proxy (main.py):
  ↓
Dodman Core API:
POST http://localhost:8080/api/auth/login
  ↓
Response flows back:
Backend → Frontend
```

**Why proxy?**
- ✅ **Security:** Hide dodman-core API URL from frontend
- ✅ **Session Management:** Set HTTP-only cookies
- ✅ **CORS:** Handle cross-origin requests
- ✅ **Middleware:** Add logging, rate limiting, etc.

---

## 🔌 API Endpoints

### **Authentication Routes** (`/auth/*`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Request magic link |
| POST | `/auth/verify` | Verify magic link token |
| POST | `/auth/logout` | Logout and clear session |
| POST | `/auth/refresh` | Refresh session token |
| GET | `/auth/session` | Get current session info |

### **Plugin Routes** (`/plugins/*`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/plugins` | List all plugins |
| GET | `/plugins/{id}` | Get plugin details |
| POST | `/plugins/{id}/execute` | Execute plugin action |
| GET | `/plugins/{id}/status` | Get plugin status |
| PUT | `/plugins/{id}/config` | Update configuration |
| POST | `/plugins/{id}/pause` | Pause plugin |
| POST | `/plugins/{id}/resume` | Resume plugin |

### **Frontend Routes**

| Path | Serves |
|------|--------|
| `/` | Main dashboard (`frontend/index.html`) |
| `/css/*` | Static CSS files |
| `/js/*` | Static JavaScript files |
| `/admin/*` | Admin pages (sandbox, settings) |
| `/sandbox/plugin/{id}` | Plugin sandbox environment |

---

## 🔐 Authentication Flow

### **1. Request Magic Link**

```javascript
// Frontend
const response = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@company.com' })
});

// Backend proxies to:
// POST http://localhost:8080/api/auth/request-magic-link
```

### **2. User Clicks Email Link**

```
Magic link: https://acme.dodman.ai/verify?token=eyJhbG...
```

### **3. Verify Token**

```javascript
// Frontend
const response = await fetch('/auth/verify', {
  method: 'POST',
  body: JSON.stringify({ token: urlParams.get('token') })
});

// Backend:
// 1. Proxies to dodman-core /api/auth/verify-magic-link
// 2. Sets HTTP-only cookies with session/refresh tokens
// 3. Returns user data
```

### **4. Authenticated Requests**

```javascript
// Frontend (cookies sent automatically)
const response = await fetch('/api/tenants/overview');

// Backend:
// 1. Reads session_token from cookie
// 2. Proxies to dodman-core with Authorization: Bearer {token}
// 3. Returns response
```

---

## 🧪 Testing

### **Health Check**

```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "master-dashboard-template",
  "version": "1.0.0",
  "core_api": "http://localhost:8080"
}
```

### **Test Magic Link**

```bash
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@acme.com"}'
```

### **Test Plugin List**

```bash
curl http://localhost:3000/plugins \
  -H "Cookie: session_token={your_token}"
```

---

## 🔧 Development

### **Auto-Reload**

The server auto-reloads when you change:
- `main.py`
- `routes/*.py`
- Frontend files (`frontend/*`)

Just save and refresh!

### **Add New Routes**

1. Create route file in `routes/`:
```python
# routes/custom.py
from fastapi import APIRouter

router = APIRouter(prefix="/custom")

@router.get("/")
async def custom_endpoint():
    return {"message": "Custom route"}
```

2. Import in `main.py`:
```python
from routes import auth, plugins, custom

app.include_router(custom.router, prefix="/api")
```

### **Add Plugin Templates**

Create plugin-specific sandbox:
```
templates/plugins/sniper/sandbox.html
```

Accessible at:
```
http://localhost:3000/sandbox/plugin/sniper
```

---

## 🚀 Production Deployment

### **Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:3000"]
```

### **Environment Variables**

```bash
DODMAN_CORE_API_URL=https://api.dodman.ai
ENVIRONMENT=production
ALLOWED_ORIGINS=https://dashboard.dodman.ai,https://*.dodman.ai
SESSION_SECRET=<random-secure-key>
```

### **HTTPS + Secure Cookies**

In production, set cookies with `secure=True`:
```python
response.set_cookie(
    key="session_token",
    value=token,
    httponly=True,
    secure=True,  # ← Only sent over HTTPS
    samesite="strict"
)
```

---

## 📊 Monitoring

### **Logs**

```bash
# View logs
tail -f logs/dashboard.log

# With Docker
docker logs -f master-dashboard
```

### **Health Checks**

```bash
# Check if server is up
curl http://localhost:3000/health

# Check dodman-core connectivity
curl http://localhost:3000/health | grep "core_api"
```

---

## 🐛 Troubleshooting

### **"Core API unavailable"**

```bash
# Check if dodman-core is running
curl http://localhost:8080/health

# Update .env
DODMAN_CORE_API_URL=http://localhost:8080
```

### **"Frontend directory not found"**

```bash
# Make sure frontend exists
ls ../frontend/index.html

# Or set custom path in .env
FRONTEND_DIR=/path/to/frontend
```

### **CORS errors**

```bash
# In development, allow all origins
ALLOWED_ORIGINS=*

# In production, restrict to your domains
ALLOWED_ORIGINS=https://dashboard.dodman.ai,https://*.dodman.ai
```

---

## 📝 Notes

- **Stateless:** Backend is stateless, all state in dodman-core API
- **Proxy Only:** No business logic here, pure proxy to dodman-core
- **Session Cookies:** HTTP-only cookies prevent XSS attacks
- **Auto-Reload:** Changes to frontend/backend reload instantly
- **Production Ready:** Includes gunicorn config for production

---

## ✅ Checklist

Before deploying:

- [ ] Set `DODMAN_CORE_API_URL` to production API
- [ ] Set `ENVIRONMENT=production`
- [ ] Set secure `SESSION_SECRET`
- [ ] Configure `ALLOWED_ORIGINS` to real domains
- [ ] Enable `secure=True` on cookies (HTTPS only)
- [ ] Set up logging
- [ ] Configure health check monitoring
- [ ] Test all API proxy routes
- [ ] Test frontend static file serving

---

**Ready to use!** 🚀