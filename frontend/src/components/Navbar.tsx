import { Link, useNavigate } from 'react-router-dom';
import { Brain, Bell, LogOut } from 'lucide-react';
import { useState, useEffect } from 'react';
import { userAPI } from '../services/api';
import './Navbar.css';

interface UserProfile {
  full_name: string;
  email: string;
  target_role?: string;
  profile_picture_url?: string;
}

const Navbar = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const response = await userAPI.getProfile();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-logo">
          <Brain size={32} color="#3b82f6" />
          <span>PrepMind</span>
        </Link>

        <div className="navbar-menu">
          <Link to="/dashboard" className="navbar-link">Dashboard</Link>
          <Link to="/resume-analyzer" className="navbar-link">Resume</Link>
          <Link to="/interview" className="navbar-link">Interviews</Link>
          <Link to="/settings" className="navbar-link">Settings</Link>
        </div>

        <div className="navbar-actions">
          <button className="navbar-icon-btn">
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>
          
          <div className="navbar-user">
            <img
              src={user?.profile_picture_url || `https://ui-avatars.com/api/?name=${user?.full_name || 'User'}&background=3b82f6&color=fff`}
              alt={user?.full_name || 'User'}
              className="navbar-avatar"
            />
            <div className="navbar-user-info">
              <span className="navbar-user-name">{user?.full_name || 'Loading...'}</span>
              <span className="navbar-user-role">{user?.target_role || 'Student'}</span>
            </div>
          </div>

          <button className="navbar-logout" onClick={handleLogout} title="Logout">
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

