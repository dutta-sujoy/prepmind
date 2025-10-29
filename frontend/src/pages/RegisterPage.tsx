import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Brain, Mail, Lock, User, Building, BookOpen, Calendar, Briefcase, AlertCircle, Github } from 'lucide-react';
import { authAPI } from '../services/api';
import './AuthPages.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    college: '',
    branch: '',
    graduation_year: new Date().getFullYear() + 1,
    target_role: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();
    if (step === 1) {
      if (!formData.email || !formData.password || !formData.full_name) {
        setError('Please fill in all required fields');
        return;
      }
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters');
        return;
      }
      setStep(2);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.register({
        ...formData,
        graduation_year: parseInt(formData.graduation_year.toString()) || undefined,
      });
      
      // Auto-login after successful registration
      const loginResponse = await authAPI.login(formData.email, formData.password);
      localStorage.setItem('access_token', loginResponse.data.access_token);
      localStorage.setItem('refresh_token', loginResponse.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(loginResponse.data.user));
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Registration error:', err);
      
      // Better error messages
      if (err.message && err.message.includes('Network error')) {
        setError('Cannot connect to server. Please make sure the backend is running on http://localhost:8000');
      } else if (err.response?.status === 400) {
        setError('Invalid registration data. Please check all fields.');
      } else if (err.response?.status === 409) {
        setError('This email is already registered. Please use a different email or try logging in.');
      } else if (err.response?.status === 422) {
        setError('Validation error. Please check your email format and password (min 8 characters).');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          setError(detail);
        } else if (Array.isArray(detail)) {
          setError(detail[0]?.msg || 'Registration failed. Please check your input.');
        } else {
          setError('Registration failed. Please try again.');
        }
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-left">
          <Link to="/" className="auth-logo">
            <Brain size={40} color="#3b82f6" />
            <span>PrepMind</span>
          </Link>
          <div className="auth-hero">
            <h1>Create your account</h1>
            <p>Start your journey to better tech preparation</p>
            <div className="auth-progress">
              <div className="progress-steps">
                <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
                  <div className="step-number">1</div>
                  <span>Account</span>
                </div>
                <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
                  <div className="step-number">2</div>
                  <span>Career Goal</span>
                </div>
                <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
                  <div className="step-number">3</div>
                  <span>Resume</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-form-container">
            <div className="auth-header">
              <h2>{step === 1 ? 'Create your account' : 'Tell us about yourself'}</h2>
              <p>{step === 1 ? 'Start your journey to better tech preparation' : 'Help us personalize your experience'}</p>
            </div>

            {error && (
              <div className="error-message">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}

            {step === 1 ? (
              <form onSubmit={handleNext} className="auth-form">
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <div className="input-wrapper">
                    <Mail size={20} />
                    <input
                      type="email"
                      id="email"
                      name="email"
                      placeholder="you@example.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-wrapper">
                    <Lock size={20} />
                    <input
                      type="password"
                      id="password"
                      name="password"
                      placeholder="Min. 8 characters"
                      value={formData.password}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="full_name">Full Name</label>
                  <div className="input-wrapper">
                    <User size={20} />
                    <input
                      type="text"
                      id="full_name"
                      name="full_name"
                      placeholder="John Doe"
                      value={formData.full_name}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="btn btn-primary btn-large">
                  Continue
                </button>
              </form>
            ) : (
              <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                  <label htmlFor="college">College</label>
                  <div className="input-wrapper">
                    <Building size={20} />
                    <input
                      type="text"
                      id="college"
                      name="college"
                      placeholder="KIIT University"
                      value={formData.college}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="branch">Branch</label>
                  <div className="input-wrapper">
                    <BookOpen size={20} />
                    <input
                      type="text"
                      id="branch"
                      name="branch"
                      placeholder="Computer Science"
                      value={formData.branch}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="graduation_year">Graduation Year</label>
                  <div className="input-wrapper">
                    <Calendar size={20} />
                    <select
                      id="graduation_year"
                      name="graduation_year"
                      value={formData.graduation_year}
                      onChange={handleChange}
                    >
                      {[...Array(11)].map((_, i) => {
                        const year = new Date().getFullYear() + i;
                        return <option key={year} value={year}>{year}</option>;
                      })}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="target_role">Target Role</label>
                  <div className="input-wrapper">
                    <Briefcase size={20} />
                    <input
                      type="text"
                      id="target_role"
                      name="target_role"
                      placeholder="Full Stack Developer"
                      value={formData.target_role}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="form-actions">
                  <button type="button" className="btn btn-secondary" onClick={() => setStep(1)}>
                    Back
                  </button>
                  <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                    {loading ? 'Creating account...' : 'Create Account'}
                  </button>
                </div>
              </form>
            )}

            {/* {step === 1 && (
              <>
                <div className="auth-divider">
                  <span>or continue with</span>
                </div>

                <div className="social-login">
                  <button className="btn-social">
                    <svg width="20" height="20" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Google
                  </button>
                  <button className="btn-social">
                    <Github size={20} />
                    GitHub
                  </button>
                </div>
              </>
            )} */}

            <div className="auth-footer">
              <p>
                Already have an account? <Link to="/login">Sign in</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

