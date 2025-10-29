import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Brain,
  FileText,
  Mic,
  TrendingUp,
  Briefcase,
  Settings,
  LogOut,
  Bell,
  Search,
  Award,
  Target,
  Calendar,
  ChevronRight,
} from 'lucide-react';
import { userAPI, interviewAPI, resumeAPI } from '../services/api';
import './Dashboard.css';

interface UserProfile {
  full_name: string;
  email: string;
  target_role?: string;
  profile_picture_url?: string;
}

interface InterviewStats {
  total_interviews: number;
  completed_interviews: number;
  average_score: number;
  recent_interviews: any[];
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [interviewStats, setInterviewStats] = useState<InterviewStats | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [profileRes, statsRes] = await Promise.all([
        userAPI.getProfile(),
        interviewAPI.getStats().catch(() => ({ data: { total_interviews: 0, completed_interviews: 0, average_score: 0 } })),
      ]);

      setUser(profileRes.data);
      setInterviewStats(statsRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Brain size={48} color="#3b82f6" />
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="dashboard-sidebar">
        <div className="sidebar-header">
          <Link to="/" className="sidebar-logo">
            <Brain size={32} color="#3b82f6" />
            <span>PrepMind</span>
          </Link>
        </div>

        <nav className="sidebar-nav">
          <Link to="/dashboard" className="nav-item active">
            <TrendingUp size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/resume-analyzer" className="nav-item">
            <FileText size={20} />
            <span>Resume Builder</span>
          </Link>
          <Link to="/interview" className="nav-item">
            <Mic size={20} />
            <span>Mock Interviews</span>
          </Link>
          <Link to="/roadmap" className="nav-item">
            <Target size={20} />
            <span>Career Roadmap</span>
          </Link>
          <Link to="/dsa-practice" className="nav-item">
            <Award size={20} />
            <span>DSA Practice</span>
          </Link>
          <Link to="/jobs" className="nav-item">
            <Briefcase size={20} />
            <span>Job Board</span>
          </Link>
          <Link to="/settings" className="nav-item">
            <Settings size={20} />
            <span>Settings</span>
          </Link>
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item" onClick={handleLogout}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Top Bar */}
        <header className="dashboard-header">
          <div className="header-search">
            <Search size={20} />
            <input type="text" placeholder="Search anything..." />
          </div>
          <div className="header-actions">
            <button className="header-icon-btn">
              <Bell size={20} />
              <span className="notification-badge">3</span>
            </button>
            <div className="user-menu">
              <img
                src={user?.profile_picture_url || `https://ui-avatars.com/api/?name=${user?.full_name}&background=3b82f6&color=fff`}
                alt={user?.full_name}
              />
              <div className="user-info">
                <span className="user-name">{user?.full_name}</span>
                <span className="user-role">{user?.target_role || 'Student'}</span>
              </div>
            </div>
            <button className="btn btn-primary">
              + Upgrade Plan
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="dashboard-content">
          <div className="content-header">
            <div>
              <h1>Your Dashboard</h1>
              <p>Track your placement preparation progress</p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                <TrendingUp size={24} />
              </div>
              <div className="stat-content">
                <h3>Overall Progress</h3>
                <div className="stat-value">75%</div>
                <p className="stat-change positive">+5% from last week</p>
              </div>
              <div className="stat-chart">
                <div className="progress-ring" style={{ '--progress': '75%' } as any}>
                  <span>Good</span>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                <Briefcase size={24} />
              </div>
              <div className="stat-content">
                <h3>Job Readiness</h3>
                <div className="stat-value">60%</div>
                <p className="stat-change">Focus on DSA!</p>
              </div>
              <div className="stat-chart">
                <div className="progress-ring" style={{ '--progress': '60%' } as any}>
                  <span>Almost</span>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
                <Mic size={24} />
              </div>
              <div className="stat-content">
                <h3>Interview Score</h3>
                <div className="stat-value">{interviewStats?.average_score || 0}%</div>
                <p className="stat-change">{interviewStats?.completed_interviews || 0} interviews completed</p>
              </div>
              <div className="stat-chart">
                <div className="progress-ring" style={{ '--progress': `${interviewStats?.average_score || 0}%` } as any}>
                  <span>Decent</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="section-grid">
            <div className="section-card">
              <div className="section-header">
                <h2>Resume Score</h2>
                <Link to="/resume-analyzer" className="section-link">
                  Improve <ChevronRight size={16} />
                </Link>
              </div>
              <div className="resume-score-content">
                <div className="score-circle">
                  <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#e2e8f0" strokeWidth="10" />
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="#3b82f6"
                      strokeWidth="10"
                      strokeDasharray="282.7"
                      strokeDashoffset="56.54"
                      strokeLinecap="round"
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="score-value">80%</div>
                </div>
                <div className="score-details">
                  <div className="score-item">
                    <span className="score-label">Content</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: '90%' }}></div>
                    </div>
                    <span className="score-number">90%</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">Format</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: '85%' }}></div>
                    </div>
                    <span className="score-number">85%</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">Keywords</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: '75%' }}></div>
                    </div>
                    <span className="score-number">75%</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">ATS Compatibility</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: '70%' }}></div>
                    </div>
                    <span className="score-number">70%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="section-card">
              <div className="section-header">
                <h2>DSA Progress</h2>
                <Link to="/dsa-practice" className="section-link">
                  View All <ChevronRight size={16} />
                </Link>
              </div>
              <div className="dsa-progress-content">
                <div className="dsa-chart">
                  <div className="dsa-donut">
                    <div className="dsa-center">
                      <span className="dsa-total">92</span>
                      <span className="dsa-label">Total</span>
                    </div>
                  </div>
                </div>
                <div className="dsa-legend">
                  <div className="legend-item">
                    <span className="legend-color" style={{ background: '#10b981' }}></span>
                    <span className="legend-label">Easy</span>
                    <span className="legend-value">48/120</span>
                  </div>
                  <div className="legend-item">
                    <span className="legend-color" style={{ background: '#f59e0b' }}></span>
                    <span className="legend-label">Medium</span>
                    <span className="legend-value">32/90</span>
                  </div>
                  <div className="legend-item">
                    <span className="legend-color" style={{ background: '#ef4444' }}></span>
                    <span className="legend-label">Hard</span>
                    <span className="legend-value">12/40</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Career Roadmap & Upcoming */}
          <div className="section-grid">
            <div className="section-card">
              <div className="section-header">
                <h2>Career Roadmap Progress</h2>
                <Link to="/roadmap" className="section-link">
                  View All <ChevronRight size={16} />
                </Link>
              </div>
              <div className="roadmap-list">
                <div className="roadmap-item completed">
                  <div className="roadmap-icon">✓</div>
                  <div className="roadmap-content">
                    <h4>Resume Preparation</h4>
                    <p>Create ATS-friendly resume with keywords</p>
                  </div>
                  <span className="roadmap-status">Completed</span>
                </div>
                <div className="roadmap-item in-progress">
                  <div className="roadmap-icon">🔄</div>
                  <div className="roadmap-content">
                    <h4>DSA Fundamentals</h4>
                    <p>Master arrays, linked lists, and basic algorithms</p>
                  </div>
                  <span className="roadmap-status">In Progress</span>
                </div>
                <div className="roadmap-item">
                  <div className="roadmap-icon">📅</div>
                  <div className="roadmap-content">
                    <h4>Advanced DSA</h4>
                    <p>Dynamic programming, graphs, and complex algorithms</p>
                  </div>
                  <span className="roadmap-status">Upcoming</span>
                </div>
              </div>
            </div>

            <div className="section-card">
              <div className="section-header">
                <h2>Mock Interview Feedback</h2>
                <Link to="/interview" className="section-link">
                  Schedule Next <ChevronRight size={16} />
                </Link>
              </div>
              <div className="interview-feedback">
                <div className="feedback-item">
                  <div className="feedback-header">
                    <span className="feedback-type">AI Technical Interview</span>
                    <span className="feedback-date">June 6, 2023</span>
                  </div>
                  <div className="feedback-scores">
                    <div className="feedback-score">
                      <span className="score-label">Technical Knowledge</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: '85%' }}></div>
                      </div>
                      <span>85%</span>
                    </div>
                    <div className="feedback-score">
                      <span className="score-label">Problem Solving</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: '78%' }}></div>
                      </div>
                      <span>78%</span>
                    </div>
                    <div className="feedback-score">
                      <span className="score-label">Communication</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: '90%' }}></div>
                      </div>
                      <span>90%</span>
                    </div>
                  </div>
                  <p className="feedback-summary">
                    "Good approach to problem-solving, but need to work on optimizing time complexity. 
                    Communication was excellent."
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Upcoming Goals */}
          <div className="section-card full-width">
            <div className="section-header">
              <h2>Upcoming Goals & Tasks</h2>
              <button className="btn btn-primary">Add New</button>
            </div>
            <div className="goals-list">
              <div className="goal-item">
                <input type="checkbox" />
                <div className="goal-content">
                  <h4>Complete 5 LeetCode medium problems</h4>
                  <p><Calendar size={14} /> Due: Jun 19</p>
                </div>
                <span className="goal-tag">DSA</span>
              </div>
              <div className="goal-item">
                <input type="checkbox" />
                <div className="goal-content">
                  <h4>Update resume with latest project</h4>
                  <p><Calendar size={14} /> Due: Jun 20</p>
                </div>
                <span className="goal-tag">Resume</span>
              </div>
              <div className="goal-item">
                <input type="checkbox" defaultChecked />
                <div className="goal-content">
                  <h4>Complete system design module</h4>
                  <p><Calendar size={14} /> Due: Jun 28</p>
                </div>
                <span className="goal-tag">Learning</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;

