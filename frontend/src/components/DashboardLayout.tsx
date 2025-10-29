import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Brain,
  FileText,
  Mic,
  TrendingUp,
  Briefcase,
  Settings,
  LogOut,
  Target,
  Award,
} from 'lucide-react';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="layout-sidebar">
        <div className="layout-sidebar-header">
          <Link to="/dashboard" className="layout-sidebar-logo">
            <Brain size={32} color="#3b82f6" />
            <span>PrepMind</span>
          </Link>
        </div>

        <nav className="layout-sidebar-nav">
          <Link to="/dashboard" className={`layout-nav-item ${isActive('/dashboard') ? 'active' : ''}`}>
            <TrendingUp size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/resume-analyzer" className={`layout-nav-item ${isActive('/resume-analyzer') ? 'active' : ''}`}>
            <FileText size={20} />
            <span>Resume Analyzer</span>
          </Link>
          <Link to="/interview" className={`layout-nav-item ${isActive('/interview') ? 'active' : ''}`}>
            <Mic size={20} />
            <span>Mock Interviews</span>
          </Link>
          <Link to="/roadmap" className={`layout-nav-item ${isActive('/roadmap') ? 'active' : ''}`}>
            <Target size={20} />
            <span>Career Roadmap</span>
          </Link>
          <Link to="/dsa-practice" className={`layout-nav-item ${isActive('/dsa-practice') ? 'active' : ''}`}>
            <Award size={20} />
            <span>DSA Practice</span>
          </Link>
          <Link to="/jobs" className={`layout-nav-item ${isActive('/jobs') ? 'active' : ''}`}>
            <Briefcase size={20} />
            <span>Job Board</span>
          </Link>
          <Link to="/settings" className={`layout-nav-item ${isActive('/settings') ? 'active' : ''}`}>
            <Settings size={20} />
            <span>Settings</span>
          </Link>
        </nav>

        <div className="layout-sidebar-footer">
          <button className="layout-logout-button" onClick={handleLogout}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="layout-main-content">
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;

