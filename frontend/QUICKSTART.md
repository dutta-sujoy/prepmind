# PrepMind Frontend - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies
```bash
cd prepmind-frontend
npm install
```

### Step 2: Configure Environment
Create a `.env` file in the root directory:
```bash
# Windows PowerShell
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Mac/Linux
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

Or manually create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Start Development Server
```bash
npm run dev
```

Visit: **http://localhost:5173**

## 🎯 Quick Navigation

- **Landing Page**: http://localhost:5173/
- **Login**: http://localhost:5173/login
- **Register**: http://localhost:5173/register
- **Dashboard**: http://localhost:5173/dashboard (requires login)
- **Mock Interview**: http://localhost:5173/interview (requires login)
- **Resume Analyzer**: http://localhost:5173/resume-analyzer (requires login)

## 🧪 Test the App

### 1. Landing Page
- ✅ Scroll through sections
- ✅ Click "Get Started Free" or "Start Free"
- ✅ Hover over feature cards
- ✅ Check responsive design (resize window)

### 2. Register New Account
- ✅ Click "Start Free" from landing page
- ✅ Fill in email, password, full name
- ✅ Click "Continue"
- ✅ Fill in college details (optional)
- ✅ Click "Create Account"

### 3. Login
- ✅ Use the email and password from registration
- ✅ Click "Sign in"

### 4. Explore Dashboard
- ✅ View progress metrics
- ✅ Check resume score
- ✅ See DSA progress
- ✅ View interview feedback
- ✅ Explore roadmap progress

### 5. Try Mock Interview
- ✅ Click "Mock Interviews" in sidebar
- ✅ Configure interview settings
- ✅ Enable/disable microphone and camera
- ✅ Click "Start Interview"
- ✅ Go through questions
- ✅ View results

### 6. Analyze Resume
- ✅ Click "Resume Builder" in sidebar
- ✅ Drag & drop a PDF/DOCX resume
- ✅ Click "Analyze Resume"
- ✅ View ATS score and feedback

## 📱 Test Responsive Design

1. **Desktop**: Default view (> 1024px)
2. **Tablet**: Resize window to ~800px width
3. **Mobile**: Resize window to ~375px width

Or use browser DevTools:
- Press F12
- Click device icon
- Select mobile device

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173
npm run dev
```

### Dependencies Error
```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors
```bash
npm run build
```

### API Connection Error
- Make sure backend is running on port 8000
- Check `.env` file has correct API URL
- Test backend: http://localhost:8000/health

## 📦 Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

Build output: `dist/` folder

## 🎨 Customize

### Update Colors
Edit `src/index.css`:
```css
:root {
  --primary-color: #3b82f6;  /* Change this */
  --secondary-color: #8b5cf6; /* Change this */
}
```

### Update Logo
Replace logo in pages:
- `src/pages/LandingPage.tsx`
- `src/pages/Dashboard.tsx`
- `src/pages/InterviewPage.tsx`

### Update API URL
Edit `.env`:
```env
VITE_API_BASE_URL=https://your-api.com
```

## 🚢 Deploy

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

### Environment Variables (Production)
Set in your hosting platform:
```
VITE_API_BASE_URL=https://api.prepmind.com
```

## 📚 Additional Resources

- **Setup Guide**: `README_SETUP.md`
- **Full Summary**: `PROJECT_SUMMARY.md`
- **Backend API**: `../backend api documentations.json`

## ⚡ Performance Tips

1. Use production build for deployment
2. Enable gzip compression on server
3. Use CDN for static assets
4. Implement lazy loading for routes
5. Add service worker for PWA

## 🐛 Common Issues

**Issue**: "Cannot find module"
**Solution**: Run `npm install`

**Issue**: "Port 5173 already in use"
**Solution**: Change port in `vite.config.ts` or kill process

**Issue**: "API request failed"
**Solution**: Check backend is running and URL is correct

**Issue**: Login redirects to login
**Solution**: Check JWT token in localStorage (DevTools > Application)

**Issue**: White screen on refresh
**Solution**: Check browser console for errors

## 💬 Support

For any issues:
1. Check browser console (F12)
2. Check terminal for errors
3. Verify backend is running
4. Review API documentation
5. Check network tab in DevTools

## ✨ Features to Try

1. **Landing Page**:
   - Smooth scroll
   - Hover animations
   - CTA buttons

2. **Dashboard**:
   - Progress metrics
   - Score visualizations
   - Roadmap tracker

3. **Interview**:
   - Question flow
   - Timer
   - Live feedback

4. **Resume**:
   - Drag & drop upload
   - Analysis animation
   - Score breakdown

## 🎯 Next Steps

1. Connect to real backend API
2. Add more pages (DSA Practice, Roadmap, Jobs)
3. Implement WebSocket for real-time features
4. Add video/audio recording
5. Implement dark mode
6. Add unit tests
7. SEO optimization
8. Analytics integration

---

**Ready to go? Run `npm run dev` and start building! 🚀**

