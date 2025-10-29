# CORS Fix Guide - PrepMind

## 🔴 Problem

You're seeing this error:
```
INFO: 127.0.0.1:61989 - "OPTIONS /api/v1/auth/login HTTP/1.1" 400 Bad Request
```

This is a **CORS (Cross-Origin Resource Sharing)** issue. The browser sends a preflight OPTIONS request, and the backend is rejecting it.

## ✅ Solution

### Option 1: Fix Backend CORS (Recommended)

Your **FastAPI backend** needs to enable CORS. Add this to your main FastAPI file:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Allow all headers
)

# Your routes here...
```

### Option 2: For Production

For production, specify exact origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://prepmind.com",
        "https://www.prepmind.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)
```

### Option 3: Development Only - Allow All Origins

⚠️ **Only for development!**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔍 Verify CORS is Working

1. Start your backend server
2. Open browser console (F12)
3. Try to login from frontend
4. Check Network tab - you should see:
   - OPTIONS request with 200 status
   - POST request with 200 status

## 📝 Complete Backend Example

```python
# main.py or app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PrepMind API",
    description="AI-powered placement preparation platform",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your routes
@app.get("/")
def root():
    return {"message": "PrepMind API"}

@app.post("/api/v1/auth/login")
def login(credentials: LoginRequest):
    # Your login logic
    pass
```

## 🧪 Test CORS

### Using cURL:
```bash
curl -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

You should see these headers in the response:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### Using Browser Console:
```javascript
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123'
  })
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err));
```

## 🔧 Alternative: Use Vite Proxy (Development Only)

If you can't modify the backend, use Vite's proxy feature:

**vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
```

Then update your `.env`:
```env
VITE_API_BASE_URL=
```

Leave it empty so API calls go to the same origin (Vite dev server), which will proxy to backend.

## 🚨 Common Mistakes

### ❌ Wrong:
```python
# Don't use both "*" and credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # ❌ This won't work!
)
```

### ✅ Correct:
```python
# Either use specific origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
)

# Or use "*" without credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
)
```

## 📋 Checklist

- [ ] Backend has CORS middleware installed
- [ ] CORS middleware is configured before routes
- [ ] Frontend origin is in `allow_origins` list
- [ ] `allow_methods` includes OPTIONS, POST, GET, etc.
- [ ] `allow_headers` includes Content-Type and Authorization
- [ ] Backend server is running
- [ ] Frontend is using correct API URL
- [ ] Browser console shows no CORS errors

## 🆘 Still Not Working?

### Check Backend Logs:
```bash
# Look for OPTIONS requests
# Should see 200, not 400 or 404
```

### Check Browser Console:
```
F12 → Console → Look for CORS errors
F12 → Network → Click on failed request → Check headers
```

### Verify Ports:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

### Test Backend Directly:
```bash
curl http://localhost:8000/health
```

## 📚 Additional Resources

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Vite Proxy Configuration](https://vitejs.dev/config/server-options.html#server-proxy)

---

## 🎯 Quick Fix Summary

**Add this to your FastAPI backend:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart your backend server and try again!**

