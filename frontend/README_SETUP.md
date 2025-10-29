# PrepMind Frontend - Setup Guide

A modern React-based AI-powered placement preparation platform built with TypeScript, Vite, and React Router.

## 🚀 Features

- **Landing Page**: Modern hero section with features showcase, testimonials, and pricing
- **Authentication**: Login and multi-step registration with social login options
- **Dashboard**: Comprehensive progress tracking with analytics and insights
- **Mock Interviews**: AI-powered interview simulator with real-time feedback
- **Resume Analyzer**: Upload and analyze resumes with ATS scoring
- **Responsive Design**: Mobile-first design that works on all devices

## 📦 Installation

1. Navigate to the project directory:
```bash
cd prepmind-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
# Create .env file in the root directory
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🏗️ Project Structure

```
prepmind-frontend/
├── src/
│   ├── pages/
│   │   ├── LandingPage.tsx       # Home page with hero and features
│   │   ├── LoginPage.tsx         # Login form
│   │   ├── RegisterPage.tsx      # Multi-step registration
│   │   ├── Dashboard.tsx         # Main dashboard
│   │   ├── InterviewPage.tsx     # Mock interview simulator
│   │   ├── ResumeAnalyzerPage.tsx # Resume upload and analysis
│   │   └── *.css                 # Page-specific styles
│   ├── services/
│   │   └── api.ts                # API service with axios
│   ├── App.tsx                   # Main app with routing
│   ├── App.css                   # App-level styles
│   ├── index.css                 # Global styles
│   └── main.tsx                  # Entry point
├── public/
├── index.html
└── package.json
```

## 🔌 API Integration

The app connects to the PrepMind backend API. Make sure the backend is running on `http://localhost:8000` or update the `VITE_API_BASE_URL` in your `.env` file.

### Available API Services:

- **authAPI**: Registration, login, logout, password management
- **userAPI**: Profile management, preferences, avatar upload
- **resumeAPI**: Resume upload, analysis, comparison
- **interviewAPI**: Interview creation, question generation, results

## 🎨 Styling

The project uses custom CSS with CSS variables for theming. Key colors:

- Primary: `#3b82f6` (Blue)
- Secondary: `#8b5cf6` (Purple)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Orange)
- Error: `#ef4444` (Red)

## 📱 Pages Overview

### 1. Landing Page (`/`)
- Hero section with CTA
- Features showcase (6 key features)
- Student testimonials
- Pricing plans (Free & Premium)
- Footer with links

### 2. Authentication
- **Login** (`/login`): Email/password with social login options
- **Register** (`/register`): 2-step registration process

### 3. Dashboard (`/dashboard`)
Protected route with:
- Overall progress metrics
- Resume score breakdown
- DSA progress tracker
- Interview feedback
- Career roadmap progress
- Upcoming goals & tasks

### 4. Mock Interview (`/interview`)
- Setup page: Configure interview type, role, difficulty
- Interview session: Real-time Q&A with timer
- Results page: Detailed performance analysis

### 5. Resume Analyzer (`/resume-analyzer`)
- File upload (drag & drop or browse)
- AI analysis with ATS scoring
- Strengths, weaknesses, and suggestions
- Keyword extraction and recommendations

## 🔐 Authentication Flow

1. User registers/logs in
2. Access token and refresh token stored in localStorage
3. Axios interceptor adds token to all requests
4. Auto-refresh on 401 errors
5. Protected routes check for token

## 🛠️ Development Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 📦 Dependencies

- **react**: ^19.1.1
- **react-dom**: ^19.1.1
- **react-router-dom**: ^7.1.3
- **axios**: ^1.7.9
- **lucide-react**: ^0.469.0 (Icons)
- **recharts**: ^2.15.1 (Charts - optional)

## 🌐 Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📝 Notes

- The app uses TypeScript for type safety
- All API calls are centralized in `src/services/api.ts`
- Protected routes redirect to login if not authenticated
- Responsive design works on mobile, tablet, and desktop
- Uses React 19 with StrictMode enabled

## 🚧 TODO

- [ ] Add WebSocket support for real-time interview
- [ ] Implement actual video/audio recording
- [ ] Add more pages (DSA Practice, Career Roadmap, Job Board)
- [ ] Implement dark mode toggle
- [ ] Add unit tests
- [ ] Add loading skeletons
- [ ] Implement notifications system

## 📄 License

This project is part of the PrepMind platform.

## 🤝 Support

For issues or questions, contact the development team.

