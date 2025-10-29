import { Link } from 'react-router-dom';
import { 
  Brain, 
  FileText, 
  Mic, 
  TrendingUp, 
  Briefcase, 
  BookOpen,
  CheckCircle,
  Star,
  ArrowRight,
  Play
} from 'lucide-react';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* Navbar */}
      <nav className="navbar">
        <div className="container">
          <div className="nav-content">
            <div className="logo">
              <Brain size={32} color="#3b82f6" />
              <span className="logo-text">PrepMind</span>
              <span className="beta-badge">BETA</span>
            </div>
            <div className="nav-links">
              <a href="#features">Features</a>
              <a href="#testimonials">Testimonials</a>
              <a href="#pricing">Pricing</a>
              <Link to="/login" className="btn-nav-login">Sign In</Link>
              <Link to="/register" className="btn btn-primary">Start Free</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text fade-in">
              <h1 className="hero-title">
                Smarter Prep.<br />
                <span className="gradient-text">Better Jobs.</span>
              </h1>
              <p className="hero-description">
                Leverage AI to prepare for tech interviews, build your resume, 
                and land your dream job. Made by engineers, for future engineers.
              </p>
              <div className="hero-actions">
                <Link to="/register" className="btn btn-primary btn-large">
                  Get Started Free <ArrowRight size={20} />
                </Link>
                <button className="btn btn-secondary btn-large">
                  <Play size={20} /> Watch Demo
                </button>
              </div>
              <div className="hero-stats">
                <div className="stat-item">
                  <div className="stat-avatars">
                    <img src="https://i.pravatar.cc/40?img=1" alt="User" />
                    <img src="https://i.pravatar.cc/40?img=2" alt="User" />
                    <img src="https://i.pravatar.cc/40?img=3" alt="User" />
                  </div>
                  <span>Join <strong>10,000+</strong> students</span>
                </div>
              </div>
            </div>
            <div className="hero-image slide-in-right">
              <div className="hero-mockup">
                <img 
                  src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&auto=format&fit=crop" 
                  alt="Students preparing" 
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">AI-Powered Tools for Your Success</h2>
            <p className="section-subtitle">
              Everything you need to ace your technical interviews and land your dream tech job
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <FileText size={32} />
              </div>
              <h3>AI Resume Reviewer</h3>
              <p>
                Get instant feedback on your resume with AI-powered suggestions 
                to make it ATS-friendly and stand out to recruiters.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Mic size={32} />
              </div>
              <h3>Mock Interviews</h3>
              <p>
                Practice with our AI interviewer that simulates real technical 
                interviews and provides instant feedback on your responses.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <BookOpen size={32} />
              </div>
              <h3>Career Roadmap</h3>
              <p>
                Personalized learning paths based on your target companies and roles, 
                with progress tracking and recommendations.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <TrendingUp size={32} />
              </div>
              <h3>DSA Practice</h3>
              <p>
                Curated collection of DSA problems with AI-assisted hints, solutions, 
                and performance tracking.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Briefcase size={32} />
              </div>
              <h3>Peer Community</h3>
              <p>
                Connect with fellow students, share experiences, and participate 
                in mock interviews with peers.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <Brain size={32} />
              </div>
              <h3>Industry Insights</h3>
              <p>
                Stay updated with the latest hiring trends, salary data, 
                and company-specific interview patterns.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Student Success Stories</h2>
            <p className="section-subtitle">
              Hear from students who landed their dream jobs with PrepMind
            </p>
          </div>
          <div className="testimonials-grid">
            <div className="testimonial-card">
              <div className="testimonial-header">
                <img src="https://i.pravatar.cc/60?img=13" alt="Arjun Mehta" />
                <div>
                  <h4>Arjun Mehta</h4>
                  <p>Software Engineer @ Google</p>
                </div>
              </div>
              <p className="testimonial-text">
                "The AI mock interviews were incredibly realistic. They helped me identify 
                my weak areas and improve my communication skills. I landed my dream job 
                at Google after just 2 months of preparation with PrepMind."
              </p>
              <div className="testimonial-rating">
                {[...Array(5)].map((_, i) => <Star key={i} size={16} fill="#fbbf24" color="#fbbf24" />)}
              </div>
            </div>
            <div className="testimonial-card">
              <div className="testimonial-header">
                <img src="https://i.pravatar.cc/60?img=30" alt="Priya Sharma" />
                <div>
                  <h4>Priya Sharma</h4>
                  <p>SDE @ Amazon</p>
                </div>
              </div>
              <p className="testimonial-text">
                "The resume reviewer gave me actionable feedback that transformed my resume. 
                The DSA practice problems were perfectly curated for my target companies. 
                PrepMind was instrumental in my journey to Amazon."
              </p>
              <div className="testimonial-rating">
                {[...Array(5)].map((_, i) => <Star key={i} size={16} fill="#fbbf24" color="#fbbf24" />)}
              </div>
            </div>
            <div className="testimonial-card">
              <div className="testimonial-header">
                <img src="https://i.pravatar.cc/60?img=33" alt="Rahul Kapoor" />
                <div>
                  <h4>Rahul Kapoor</h4>
                  <p>Frontend Developer @ Microsoft</p>
                </div>
              </div>
              <p className="testimonial-text">
                "As someone with social anxiety, the AI interviews were a game-changer. 
                I could practice at my own pace without the pressure of real people. 
                The personalized roadmap kept me focused throughout my preparation."
              </p>
              <div className="testimonial-rating">
                {[...Array(5)].map((_, i) => <Star key={i} size={16} fill="#fbbf24" color="#fbbf24" />)}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="pricing-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Simple, Transparent Pricing</h2>
            <p className="section-subtitle">Start for free, upgrade when you're ready</p>
          </div>
          <div className="pricing-grid">
            <div className="pricing-card">
              <h3>Free</h3>
              <p className="pricing-subtitle">Perfect for getting started</p>
              <div className="price">
                <span className="price-amount">$0</span>
                <span className="price-period">/month</span>
              </div>
              <ul className="pricing-features">
                <li><CheckCircle size={20} /> Basic DSA practice (100 problems)</li>
                <li><CheckCircle size={20} /> 1 AI resume review per month</li>
                <li><CheckCircle size={20} /> 3 AI mock interviews per month</li>
                <li><CheckCircle size={20} /> Community access</li>
              </ul>
              <Link to="/register" className="btn btn-secondary btn-large">Get Started</Link>
            </div>
            <div className="pricing-card pricing-card-popular">
              <div className="popular-badge">POPULAR</div>
              <h3>Premium</h3>
              <p className="pricing-subtitle">For serious job seekers</p>
              <div className="price">
                <span className="price-amount">$19</span>
                <span className="price-period">/month</span>
              </div>
              <ul className="pricing-features">
                <li><CheckCircle size={20} /> Unlimited DSA practice (350+ problems)</li>
                <li><CheckCircle size={20} /> Unlimited AI resume reviews</li>
                <li><CheckCircle size={20} /> Unlimited AI mock interviews</li>
                <li><CheckCircle size={20} /> Personalized career roadmap</li>
                <li><CheckCircle size={20} /> Company-specific interview prep</li>
                <li><CheckCircle size={20} /> Priority community support</li>
              </ul>
              <Link to="/register" className="btn btn-primary btn-large">Start 7-Day Free Trial</Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Join thousands preparing smarter with AI</h2>
            <p>
              Get started today and increase your chances of landing your dream tech job
            </p>
            <div className="cta-actions">
              <Link to="/register" className="btn btn-primary btn-large">
                Get Started Free <ArrowRight size={20} />
              </Link>
              <Link to="/login" className="btn btn-secondary btn-large">
                Schedule a Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-logo">
                <Brain size={32} color="#3b82f6" />
                <span>PrepMind</span>
              </div>
              <p>© 2025 PrepMind. All rights reserved.</p>
            </div>
            <div className="footer-links">
              <div className="footer-column">
                <h4>Product</h4>
                <a href="#features">Features</a>
                <a href="#pricing">Pricing</a>
                <a href="#testimonials">Testimonials</a>
              </div>
              <div className="footer-column">
                <h4>Company</h4>
                <a href="#about">About</a>
                <a href="#contact">Contact</a>
                <a href="#careers">Careers</a>
              </div>
              <div className="footer-column">
                <h4>Legal</h4>
                <a href="#privacy">Privacy</a>
                <a href="#terms">Terms</a>
                <a href="#help">Help</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

