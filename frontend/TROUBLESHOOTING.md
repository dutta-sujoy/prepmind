# Troubleshooting Guide - PrepMind Frontend

## 🔴 Login/Register Issues

### Error: "OPTIONS /api/v1/auth/login HTTP/1.1" 400 Bad Request

**Cause**: CORS (Cross-Origin Resource Sharing) is not enabled on the backend.

**Solution**: Add CORS middleware to your FastAPI backend:

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

See `CORS_FIX.md` for detailed instructions.

---

### Error: "Cannot connect to server"

**Possible Causes**:
1. Backend is not running
2. Backend is running on wrong port
3. Wrong API URL in `.env`

**Solutions**:

1. **Check if backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return a response. If not, start your backend.

2. **Verify backend port**:
   Check your backend logs - it should show:
   ```
   INFO: Uvicorn running on http://127.0.0.1:8000
   ```

3. **Check `.env` file**:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```
   Make sure there's no trailing slash!

4. **Restart frontend**:
   ```bash
   # Stop the dev server (Ctrl+C)
   npm run dev
   ```

---

### Error: "Invalid email or password format"

**Cause**: Backend validation is rejecting the input.

**Solutions**:

1. **Email format**: Must be valid email (e.g., `user@example.com`)
2. **Password**: Must be at least 8 characters
3. **Check backend logs** for exact validation error

---

### Error: "This email is already registered"

**Cause**: Email already exists in database.

**Solutions**:
1. Use a different email
2. Try logging in instead
3. Or delete the user from database (development only)

---

## 🔴 Dashboard Issues

### Error: Dashboard shows "Loading..." forever

**Possible Causes**:
1. Not logged in
2. Invalid token
3. Backend API not responding

**Solutions**:

1. **Check if logged in**:
   - Open DevTools (F12)
   - Go to Application → Local Storage
   - Check if `access_token` exists

2. **Clear tokens and re-login**:
   ```javascript
   // In browser console
   localStorage.clear();
   // Then go to /login
   ```

3. **Check API calls**:
   - Open DevTools → Network tab
   - Look for failed requests
   - Check error messages

---

### Error: "401 Unauthorized" on dashboard

**Cause**: Token expired or invalid.

**Solution**:
1. Logout and login again
2. Or clear localStorage:
   ```javascript
   localStorage.clear();
   ```

---

## 🔴 Interview Page Issues

### Error: "Failed to create interview"

**Possible Causes**:
1. Backend interview endpoint not working
2. Invalid input data
3. Missing required fields

**Solutions**:

1. **Check console logs** (F12 → Console)
2. **Verify all fields are filled**:
   - Interview type
   - Target role
   - Technologies (at least one)
   - Difficulty
   - Number of questions

3. **Check backend logs** for error details

---

### Camera/Microphone not working

**Cause**: Browser permissions not granted.

**Solutions**:

1. **Grant permissions**:
   - Click the camera icon in address bar
   - Allow camera and microphone

2. **Check browser settings**:
   - Chrome: Settings → Privacy → Site Settings → Camera/Microphone
   - Firefox: Preferences → Privacy & Security → Permissions

3. **Use HTTPS** (required for some browsers):
   - Or use localhost (which is allowed)

---

## 🔴 Resume Analyzer Issues

### Error: "File size must be less than 5MB"

**Solution**: Compress your PDF or use a smaller file.

---

### Error: "Only PDF and DOCX files are supported"

**Solution**: Convert your resume to PDF or DOCX format.

---

### Error: "Failed to upload resume"

**Possible Causes**:
1. Backend upload endpoint not working
2. File too large
3. Invalid file format

**Solutions**:

1. **Check file size**: Max 5MB
2. **Check file type**: Must be `.pdf` or `.docx`
3. **Check backend logs** for upload errors
4. **Try a different file**

---

## 🔴 General Issues

### White screen / Blank page

**Possible Causes**:
1. JavaScript error
2. Build error
3. Route not found

**Solutions**:

1. **Check browser console** (F12):
   - Look for red errors
   - Fix any JavaScript errors

2. **Clear cache**:
   - Ctrl+Shift+R (hard refresh)
   - Or clear browser cache

3. **Rebuild**:
   ```bash
   npm run build
   npm run preview
   ```

---

### Styles not loading / Broken UI

**Solutions**:

1. **Hard refresh**: Ctrl+Shift+R
2. **Clear Vite cache**:
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```
3. **Check CSS files** are imported correctly

---

### "Module not found" errors

**Solutions**:

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Delete and reinstall**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

---

### Port 5173 already in use

**Solutions**:

1. **Kill the process**:
   ```bash
   # Windows
   npx kill-port 5173
   
   # Mac/Linux
   lsof -ti:5173 | xargs kill -9
   ```

2. **Use different port**:
   Edit `vite.config.ts`:
   ```typescript
   export default defineConfig({
     server: {
       port: 3000
     }
   })
   ```

---

## 🔍 Debugging Tips

### 1. Check Browser Console
```
F12 → Console tab
Look for red errors
```

### 2. Check Network Tab
```
F12 → Network tab
Filter by XHR/Fetch
Click on failed requests
Check Response tab
```

### 3. Check Backend Logs
```bash
# Your backend should show logs like:
INFO: 127.0.0.1:61989 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

### 4. Check LocalStorage
```
F12 → Application → Local Storage → http://localhost:5173
Check: access_token, refresh_token, user
```

### 5. Test API Directly
```bash
# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## 🆘 Still Having Issues?

### Checklist:

- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 5173
- [ ] CORS is enabled on backend
- [ ] `.env` file exists with correct API URL
- [ ] Dependencies are installed (`npm install`)
- [ ] Browser console shows no errors
- [ ] Network tab shows successful API calls

### Get Help:

1. **Check backend logs** for errors
2. **Check browser console** for JavaScript errors
3. **Check network tab** for failed API calls
4. **Try with a fresh browser** (incognito mode)
5. **Clear all caches** and restart

### Common Commands:

```bash
# Restart everything
npm run dev

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if backend is running
curl http://localhost:8000/health

# Kill port 5173
npx kill-port 5173
```

---

## 📚 Additional Resources

- **CORS Fix**: See `CORS_FIX.md`
- **Setup Guide**: See `README_SETUP.md`
- **Quick Start**: See `QUICKSTART.md`
- **API Docs**: See `../backend api documentations.json`

---

## 🎯 Quick Fixes

### Can't login?
1. Check backend is running
2. Enable CORS on backend
3. Check email/password format

### Dashboard not loading?
1. Clear localStorage
2. Login again
3. Check API calls in Network tab

### Interview not starting?
1. Fill all required fields
2. Check backend logs
3. Grant camera/mic permissions

### Resume upload failing?
1. Check file size (< 5MB)
2. Use PDF or DOCX only
3. Check backend upload endpoint

---

**Still stuck? Check the browser console (F12) and backend logs for detailed error messages!**

