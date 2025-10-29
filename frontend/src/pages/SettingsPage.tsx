import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Mail,
  Building,
  GraduationCap,
  Briefcase,
  Lock,
  Bell,
  Globe,
  Trash2,
  Save,
  Camera,
  Linkedin,
  Github,
  ExternalLink,
  Phone,
  FileText,
  Code,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { userAPI, authAPI } from '../services/api';
import './SettingsPage.css';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  college?: string;
  branch?: string;
  graduation_year?: number;
  target_role?: string;
  profile_picture_url?: string;
  bio?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
}

interface UserPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  job_alerts: boolean;
  roadmap_reminders: boolean;
  interview_reminders: boolean;
  theme: string;
  language: string;
  profile_visibility: string;
  show_progress_publicly: boolean;
}

interface PlatformIntegrations {
  leetcode_username?: string;
  github_username?: string;
  hackerrank_username?: string;
  codechef_username?: string;
  gfg_username?: string;
}

const SettingsPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Profile State
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    college: '',
    branch: '',
    graduation_year: '',
    target_role: '',
    bio: '',
    phone: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
  });

  // Password State
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Preferences State
  const [preferences, setPreferences] = useState<UserPreferences>({
    email_notifications: true,
    push_notifications: true,
    job_alerts: true,
    roadmap_reminders: true,
    interview_reminders: true,
    theme: 'light',
    language: 'en',
    profile_visibility: 'private',
    show_progress_publicly: false,
  });

  // Integrations State
  const [integrations, setIntegrations] = useState<PlatformIntegrations>({
    leetcode_username: '',
    github_username: '',
    hackerrank_username: '',
    codechef_username: '',
    gfg_username: '',
  });

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const [profileRes, preferencesRes, integrationsRes] = await Promise.all([
        userAPI.getProfile(),
        userAPI.getPreferences(),
        userAPI.getIntegrations(),
      ]);

      const profileData = profileRes.data;
      setProfile(profileData);
      setProfileForm({
        full_name: profileData.full_name || '',
        college: profileData.college || '',
        branch: profileData.branch || '',
        graduation_year: profileData.graduation_year?.toString() || '',
        target_role: profileData.target_role || '',
        bio: profileData.bio || '',
        phone: profileData.phone || '',
        linkedin_url: profileData.linkedin_url || '',
        github_url: profileData.github_url || '',
        portfolio_url: profileData.portfolio_url || '',
      });

      setPreferences(preferencesRes.data);
      setIntegrations(integrationsRes.data);
    } catch (error) {
      console.error('Error loading user data:', error);
      showMessage('error', 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data: any = {
        full_name: profileForm.full_name,
        college: profileForm.college?.trim() || null,
        branch: profileForm.branch?.trim() || null,
        graduation_year: profileForm.graduation_year ? parseInt(profileForm.graduation_year) : null,
        target_role: profileForm.target_role?.trim() || null,
        bio: profileForm.bio?.trim() || null,
        phone: profileForm.phone?.trim() || null,
        linkedin_url: profileForm.linkedin_url?.trim() || null,
        github_url: profileForm.github_url?.trim() || null,
        portfolio_url: profileForm.portfolio_url?.trim() || null,
      };

      await userAPI.updateProfile(data);
      showMessage('success', 'Profile updated successfully!');
      loadUserData();
    } catch (error: any) {
      console.error('Error updating profile:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      showMessage('error', 'Passwords do not match');
      return;
    }
    if (passwordForm.new_password.length < 8) {
      showMessage('error', 'Password must be at least 8 characters');
      return;
    }

    setSaving(true);
    try {
      await authAPI.changePassword(passwordForm.current_password, passwordForm.new_password);
      showMessage('success', 'Password changed successfully!');
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error: any) {
      console.error('Error changing password:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to change password');
    } finally {
      setSaving(false);
    }
  };

  const handlePreferencesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await userAPI.updatePreferences(preferences);
      showMessage('success', 'Preferences updated successfully!');
    } catch (error: any) {
      console.error('Error updating preferences:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to update preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleIntegrationsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        leetcode_username: integrations.leetcode_username?.trim() || null,
        github_username: integrations.github_username?.trim() || null,
        hackerrank_username: integrations.hackerrank_username?.trim() || null,
        codechef_username: integrations.codechef_username?.trim() || null,
        gfg_username: integrations.gfg_username?.trim() || null,
      };
      await userAPI.connectPlatforms(data);
      showMessage('success', 'Platform integrations updated successfully!');
    } catch (error: any) {
      console.error('Error updating integrations:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to update integrations');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      showMessage('error', 'Please upload a valid image file (JPEG, PNG, GIF, or WEBP)');
      e.target.value = ''; // Reset input
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      showMessage('error', 'File size must be less than 5MB');
      e.target.value = ''; // Reset input
      return;
    }

    setUploadingAvatar(true);
    try {
      await userAPI.uploadAvatar(file);
      showMessage('success', 'Profile picture updated successfully!');
      await loadUserData();
      e.target.value = ''; // Reset input after successful upload
    } catch (error: any) {
      console.error('Error uploading avatar:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to upload profile picture');
      e.target.value = ''; // Reset input
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    try {
      await userAPI.deleteAccount();
      localStorage.clear();
      navigate('/');
    } catch (error: any) {
      console.error('Error deleting account:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to delete account');
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="settings-page">
        <div className="settings-container">
          {message && (
            <div className={`alert alert-${message.type}`}>
              {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
              <span>{message.text}</span>
            </div>
          )}

          <div className="settings-content">
            <div className="settings-sidebar">
              <button
                className={`settings-tab ${activeTab === 'profile' ? 'active' : ''}`}
                onClick={() => setActiveTab('profile')}
              >
                <User size={20} />
                <span>Profile</span>
              </button>
              <button
                className={`settings-tab ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <Lock size={20} />
                <span>Security</span>
              </button>
              <button
                className={`settings-tab ${activeTab === 'integrations' ? 'active' : ''}`}
                onClick={() => setActiveTab('integrations')}
              >
                <Code size={20} />
                <span>Integrations</span>
              </button>
              <button
                className={`settings-tab ${activeTab === 'preferences' ? 'active' : ''}`}
                onClick={() => setActiveTab('preferences')}
              >
                <Bell size={20} />
                <span>Preferences</span>
              </button>
              <button
                className={`settings-tab ${activeTab === 'account' ? 'active' : ''}`}
                onClick={() => setActiveTab('account')}
              >
                <Trash2 size={20} />
                <span>Account</span>
              </button>
            </div>

            <div className="settings-main">
              {activeTab === 'profile' && (
                <div className="settings-section">
                  <h2>Profile Information</h2>
                  <p className="section-description">Update your personal information and profile details</p>

                  {/* Profile Picture */}
                  <div className="profile-picture-section">
                    <div className="avatar-container">
                      {profile?.profile_picture_url ? (
                        <img src={profile.profile_picture_url} alt="Profile" className="avatar-large" />
                      ) : (
                        <div className="avatar-large avatar-placeholder">
                          {profile?.full_name?.charAt(0).toUpperCase()}
                        </div>
                      )}
                      {uploadingAvatar && (
                        <div className="avatar-uploading-overlay">
                          <div className="spinner-small"></div>
                        </div>
                      )}
                      <label className={`avatar-upload-btn ${uploadingAvatar ? 'disabled' : ''}`}>
                        <Camera size={20} />
                        <input 
                          type="file" 
                          accept="image/jpeg,image/jpg,image/png,image/gif,image/webp" 
                          onChange={handleAvatarUpload} 
                          disabled={uploadingAvatar}
                          hidden 
                        />
                      </label>
                    </div>
                    <div>
                      <h3>{profile?.full_name}</h3>
                      <p className="text-muted">{profile?.email}</p>
                    </div>
                  </div>

                  <form onSubmit={handleProfileSubmit} className="settings-form">
                    <div className="form-row">
                      <div className="form-group">
                        <label>
                          <User size={18} />
                          Full Name *
                        </label>
                        <input
                          type="text"
                          value={profileForm.full_name}
                          onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                          required
                          minLength={2}
                          maxLength={255}
                        />
                      </div>
                      <div className="form-group">
                        <label>
                          <Mail size={18} />
                          Email
                        </label>
                        <input type="email" value={profile?.email} disabled />
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>
                          <Building size={18} />
                          College/University
                        </label>
                        <input
                          type="text"
                          value={profileForm.college}
                          onChange={(e) => setProfileForm({ ...profileForm, college: e.target.value })}
                          placeholder="e.g., KIIT University"
                        />
                      </div>
                      <div className="form-group">
                        <label>
                          <GraduationCap size={18} />
                          Branch/Stream
                        </label>
                        <input
                          type="text"
                          value={profileForm.branch}
                          onChange={(e) => setProfileForm({ ...profileForm, branch: e.target.value })}
                          placeholder="e.g., Computer Science"
                        />
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>
                          <GraduationCap size={18} />
                          Graduation Year
                        </label>
                        <input
                          type="number"
                          value={profileForm.graduation_year}
                          onChange={(e) => setProfileForm({ ...profileForm, graduation_year: e.target.value })}
                          min={2020}
                          max={2030}
                          placeholder="2025"
                        />
                      </div>
                      <div className="form-group">
                        <label>
                          <Briefcase size={18} />
                          Target Role
                        </label>
                        <input
                          type="text"
                          value={profileForm.target_role}
                          onChange={(e) => setProfileForm({ ...profileForm, target_role: e.target.value })}
                          placeholder="e.g., Full Stack Developer"
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>
                        <FileText size={18} />
                        Bio
                      </label>
                      <textarea
                        value={profileForm.bio}
                        onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                        rows={4}
                        placeholder="Tell us about yourself..."
                      />
                    </div>

                    <div className="form-group">
                      <label>
                        <Phone size={18} />
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        value={profileForm.phone}
                        onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                        placeholder="+1 234 567 8900"
                      />
                    </div>

                    <h3>Social Links</h3>
                    <div className="form-group">
                      <label>
                        <Linkedin size={18} />
                        LinkedIn URL
                      </label>
                      <input
                        type="text"
                        value={profileForm.linkedin_url}
                        onChange={(e) => setProfileForm({ ...profileForm, linkedin_url: e.target.value })}
                        placeholder="https://linkedin.com/in/yourprofile"
                      />
                      <small className="form-hint">Leave empty if you don't have one</small>
                    </div>

                    <div className="form-group">
                      <label>
                        <Github size={18} />
                        GitHub URL
                      </label>
                      <input
                        type="text"
                        value={profileForm.github_url}
                        onChange={(e) => setProfileForm({ ...profileForm, github_url: e.target.value })}
                        placeholder="https://github.com/yourusername"
                      />
                      <small className="form-hint">Leave empty if you don't have one</small>
                    </div>

                    <div className="form-group">
                      <label>
                        <Globe size={18} />
                        Portfolio URL
                      </label>
                      <input
                        type="text"
                        value={profileForm.portfolio_url}
                        onChange={(e) => setProfileForm({ ...profileForm, portfolio_url: e.target.value })}
                        placeholder="https://yourportfolio.com"
                      />
                      <small className="form-hint">Leave empty if you don't have one</small>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={saving}>
                      <Save size={20} />
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </form>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="settings-section">
                  <h2>Security Settings</h2>
                  <p className="section-description">Manage your password and security preferences</p>

                  <form onSubmit={handlePasswordSubmit} className="settings-form">
                    <div className="form-group">
                      <label>
                        <Lock size={18} />
                        Current Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.current_password}
                        onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label>
                        <Lock size={18} />
                        New Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.new_password}
                        onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                        required
                        minLength={8}
                        placeholder="Minimum 8 characters"
                      />
                    </div>

                    <div className="form-group">
                      <label>
                        <Lock size={18} />
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.confirm_password}
                        onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                        required
                        minLength={8}
                      />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={saving}>
                      <Save size={20} />
                      {saving ? 'Changing...' : 'Change Password'}
                    </button>
                  </form>
                </div>
              )}

              {activeTab === 'integrations' && (
                <div className="settings-section">
                  <h2>Platform Integrations</h2>
                  <p className="section-description">Connect your coding profiles to track progress</p>

                  <form onSubmit={handleIntegrationsSubmit} className="settings-form">
                    <div className="form-group">
                      <label>
                        <ExternalLink size={18} />
                        LeetCode Username
                      </label>
                      <input
                        type="text"
                        value={integrations.leetcode_username || ''}
                        onChange={(e) => setIntegrations({ ...integrations, leetcode_username: e.target.value })}
                        placeholder="yourusername"
                      />
                      <small className="form-hint">Your LeetCode profile username</small>
                    </div>

                    <div className="form-group">
                      <label>
                        <Github size={18} />
                        GitHub Username
                      </label>
                      <input
                        type="text"
                        value={integrations.github_username || ''}
                        onChange={(e) => setIntegrations({ ...integrations, github_username: e.target.value })}
                        placeholder="yourusername"
                      />
                      <small className="form-hint">Your GitHub profile username</small>
                    </div>

                    <div className="form-group">
                      <label>
                        <ExternalLink size={18} />
                        HackerRank Username
                      </label>
                      <input
                        type="text"
                        value={integrations.hackerrank_username || ''}
                        onChange={(e) => setIntegrations({ ...integrations, hackerrank_username: e.target.value })}
                        placeholder="yourusername"
                      />
                      <small className="form-hint">Your HackerRank profile username</small>
                    </div>

                    <div className="form-group">
                      <label>
                        <ExternalLink size={18} />
                        CodeChef Username
                      </label>
                      <input
                        type="text"
                        value={integrations.codechef_username || ''}
                        onChange={(e) => setIntegrations({ ...integrations, codechef_username: e.target.value })}
                        placeholder="yourusername"
                      />
                      <small className="form-hint">Your CodeChef profile username</small>
                    </div>

                    <div className="form-group">
                      <label>
                        <ExternalLink size={18} />
                        GeeksforGeeks Username
                      </label>
                      <input
                        type="text"
                        value={integrations.gfg_username || ''}
                        onChange={(e) => setIntegrations({ ...integrations, gfg_username: e.target.value })}
                        placeholder="yourusername"
                      />
                      <small className="form-hint">Your GeeksforGeeks profile username</small>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={saving}>
                      <Save size={20} />
                      {saving ? 'Saving...' : 'Save Integrations'}
                    </button>
                  </form>
                </div>
              )}

              {activeTab === 'preferences' && (
                <div className="settings-section">
                  <h2>Preferences</h2>
                  <p className="section-description">Customize your experience</p>

                  <form onSubmit={handlePreferencesSubmit} className="settings-form">
                    <h3>Notifications</h3>
                    <div className="toggle-group">
                      <div className="toggle-item">
                        <div>
                          <strong>Email Notifications</strong>
                          <p>Receive email updates about your progress</p>
                        </div>
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={preferences.email_notifications}
                            onChange={(e) => setPreferences({ ...preferences, email_notifications: e.target.checked })}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                      </div>

                      <div className="toggle-item">
                        <div>
                          <strong>Push Notifications</strong>
                          <p>Get browser notifications</p>
                        </div>
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={preferences.push_notifications}
                            onChange={(e) => setPreferences({ ...preferences, push_notifications: e.target.checked })}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                      </div>

                      <div className="toggle-item">
                        <div>
                          <strong>Job Alerts</strong>
                          <p>Receive notifications about new job opportunities</p>
                        </div>
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={preferences.job_alerts}
                            onChange={(e) => setPreferences({ ...preferences, job_alerts: e.target.checked })}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                      </div>

                      <div className="toggle-item">
                        <div>
                          <strong>Roadmap Reminders</strong>
                          <p>Get reminded about your learning roadmap</p>
                        </div>
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={preferences.roadmap_reminders}
                            onChange={(e) => setPreferences({ ...preferences, roadmap_reminders: e.target.checked })}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                      </div>

                      <div className="toggle-item">
                        <div>
                          <strong>Interview Reminders</strong>
                          <p>Receive reminders for scheduled interviews</p>
                        </div>
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={preferences.interview_reminders}
                            onChange={(e) => setPreferences({ ...preferences, interview_reminders: e.target.checked })}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                      </div>
                    </div>

                    <h3>Appearance</h3>
                    <div className="form-group">
                      <label>Theme</label>
                      <select
                        value={preferences.theme}
                        onChange={(e) => setPreferences({ ...preferences, theme: e.target.value })}
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="auto">Auto</option>
                      </select>
                    </div>

                    <h3>Privacy</h3>
                    <div className="form-group">
                      <label>Profile Visibility</label>
                      <select
                        value={preferences.profile_visibility}
                        onChange={(e) => setPreferences({ ...preferences, profile_visibility: e.target.value })}
                      >
                        <option value="private">Private</option>
                        <option value="public">Public</option>
                      </select>
                    </div>

                    <div className="toggle-item">
                      <div>
                        <strong>Show Progress Publicly</strong>
                        <p>Allow others to see your learning progress</p>
                      </div>
                      <label className="toggle">
                        <input
                          type="checkbox"
                          checked={preferences.show_progress_publicly}
                          onChange={(e) => setPreferences({ ...preferences, show_progress_publicly: e.target.checked })}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={saving}>
                      <Save size={20} />
                      {saving ? 'Saving...' : 'Save Preferences'}
                    </button>
                  </form>
                </div>
              )}

              {activeTab === 'account' && (
                <div className="settings-section">
                  <h2>Account Management</h2>
                  <p className="section-description">Manage your account</p>

                  <div className="danger-zone">
                    <h3>Danger Zone</h3>
                    <p>Once you delete your account, there is no going back. Please be certain.</p>
                    <button className="btn btn-danger" onClick={handleDeleteAccount}>
                      <Trash2 size={20} />
                      Delete Account
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;

