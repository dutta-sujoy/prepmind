-- ============================================
-- PREPMIND DATABASE SCHEMA
-- PostgreSQL (Supabase)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================
-- 1. USERS TABLE
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    
    -- Profile Information
    college VARCHAR(255),
    branch VARCHAR(100), -- CS, IT, ECE, etc.
    graduation_year INTEGER,
    target_role VARCHAR(100), -- SDE, ML Engineer, Data Scientist
    profile_picture_url TEXT,
    bio TEXT,
    
    -- Contact
    phone VARCHAR(20),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    
    -- Platform Integrations
    leetcode_username VARCHAR(100),
    github_username VARCHAR(100),
    hackerrank_username VARCHAR(100),
    codechef_username VARCHAR(100),
    gfg_username VARCHAR(100),
    
    -- Status & Metadata
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    subscription_expires_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================
-- 2. USER PREFERENCES
-- ============================================

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification Preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    job_alerts BOOLEAN DEFAULT TRUE,
    roadmap_reminders BOOLEAN DEFAULT TRUE,
    interview_reminders BOOLEAN DEFAULT TRUE,
    
    -- UI Preferences
    theme VARCHAR(20) DEFAULT 'light', -- light, dark, auto
    language VARCHAR(10) DEFAULT 'en',
    
    -- Privacy
    profile_visibility VARCHAR(20) DEFAULT 'private', -- private, public
    show_progress_publicly BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- ============================================
-- 3. RESUMES
-- ============================================

CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- File Information
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER, -- in bytes
    file_type VARCHAR(20), -- pdf, docx
    
    -- Extracted Content
    raw_text TEXT,
    parsed_data JSONB, -- Structured resume data (name, email, skills, experience, education, projects)
    
    -- Analysis Results
    ats_score INTEGER CHECK (ats_score >= 0 AND ats_score <= 100),
    analysis_result JSONB, -- AI feedback, suggestions, missing sections
    
    -- Metadata
    is_primary BOOLEAN DEFAULT FALSE, -- User's main resume
    version INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_created_at ON resumes(created_at DESC);

-- ============================================
-- 4. INTERVIEWS
-- ============================================

CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Interview Configuration
    interview_type VARCHAR(20) NOT NULL, -- technical, hr, behavioral, mixed
    target_role VARCHAR(100) NOT NULL,
    technologies TEXT[], -- ARRAY of technologies
    difficulty VARCHAR(20), -- easy, medium, hard
    num_questions INTEGER NOT NULL,
    
    -- Questions (Pre-generated)
    questions JSONB, -- Array of question objects with id, text, category, expected_answer
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, in_progress, completed, abandoned
    
    -- Session Metadata
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER, -- Total time taken
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_interviews_user_id ON interviews(user_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_created_at ON interviews(created_at DESC);

-- ============================================
-- 5. INTERVIEW RESULTS
-- ============================================

CREATE TABLE interview_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID REFERENCES interviews(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Overall Scoring
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    question_scores INTEGER[], -- Array of scores for each question
    
    -- Detailed Feedback
    summary TEXT,
    detailed_feedback JSONB, -- {technical_depth, communication, problem_solving, confidence}
    improvement_areas TEXT[],
    strengths TEXT[],
    
    -- Transcript
    transcript JSONB, -- Array of {question_number, question_text, answer_text, score, feedback}
    
    -- Voice Analysis
    voice_analysis JSONB, -- {pace_wpm, filler_words, confidence_score, clarity, pitch_variance}
    
    -- AI Remarks
    ai_remarks TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_interview_results_user_id ON interview_results(user_id);
CREATE INDEX idx_interview_results_interview_id ON interview_results(interview_id);
CREATE INDEX idx_interview_results_created_at ON interview_results(created_at DESC);

-- ============================================
-- 6. CAREER ROADMAPS
-- ============================================

CREATE TABLE career_roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    
    -- Roadmap Configuration
    target_role VARCHAR(100) NOT NULL,
    duration_weeks INTEGER NOT NULL,
    difficulty_level VARCHAR(20), -- beginner, intermediate, advanced
    
    -- Content
    roadmap_data JSONB NOT NULL, -- Weekly breakdown, milestones, resources
    /*
    Structure:
    {
      "weeks": [
        {
          "week_number": 1,
          "title": "DSA Fundamentals",
          "topics": ["Arrays", "Strings"],
          "resources": [{title, url, type}],
          "projects": ["Build CLI calculator"],
          "milestones": ["Complete 20 easy problems"],
          "estimated_hours": 15
        }
      ]
    }
    */
    
    -- Progress Tracking
    current_week INTEGER DEFAULT 1,
    completed_weeks INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    overall_progress INTEGER DEFAULT 0, -- 0-100%
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, abandoned
    
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_roadmaps_user_id ON career_roadmaps(user_id);
CREATE INDEX idx_roadmaps_status ON career_roadmaps(status);
CREATE INDEX idx_roadmaps_created_at ON career_roadmaps(created_at DESC);

-- ============================================
-- 7. ROADMAP MILESTONES (Tracking)
-- ============================================

CREATE TABLE roadmap_milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID REFERENCES career_roadmaps(id) ON DELETE CASCADE,
    
    week_number INTEGER NOT NULL,
    milestone_text TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_milestones_roadmap_id ON roadmap_milestones(roadmap_id);

-- ============================================
-- 8. SKILL PROGRESS (Dashboard Data)
-- ============================================

CREATE TABLE skill_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Platform
    platform VARCHAR(50) NOT NULL, -- leetcode, github, hackerrank, codechef, gfg
    
    -- Stats (Platform-specific JSONB)
    stats JSONB NOT NULL,
    /*
    LeetCode Example:
    {
      "total_solved": 250,
      "easy": 100,
      "medium": 120,
      "hard": 30,
      "topics": {"arrays": 50, "dp": 30},
      "contest_rating": 1800,
      "streak": 15
    }
    
    GitHub Example:
    {
      "total_repos": 25,
      "contributions_last_year": 500,
      "languages": {"Python": 45, "JavaScript": 30},
      "most_starred_repo": "project-name",
      "total_stars": 150
    }
    */
    
    -- Sync Metadata
    last_synced_at TIMESTAMP DEFAULT NOW(),
    sync_status VARCHAR(20) DEFAULT 'success', -- success, failed, pending
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_skill_progress_user_id ON skill_progress(user_id);
CREATE INDEX idx_skill_progress_platform ON skill_progress(platform);

-- ============================================
-- 9. PROJECTS (User's Projects)
-- ============================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Project Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tech_stack TEXT[], -- ["React", "Node.js", "MongoDB"]
    category VARCHAR(50), -- web, mobile, ml, blockchain, etc.
    
    -- Links
    github_url VARCHAR(255),
    live_demo_url VARCHAR(255),
    
    -- Resume Description (AI-generated)
    resume_description TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'in_progress', -- planned, in_progress, completed
    
    -- Metadata
    started_at DATE,
    completed_at DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);

-- ============================================
-- 10. COVER LETTERS
-- ============================================

CREATE TABLE cover_letters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    
    -- Job Details
    company_name VARCHAR(255),
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT,
    
    -- Content
    content TEXT NOT NULL,
    tone VARCHAR(20), -- professional, enthusiastic, formal, casual
    
    -- File
    file_url TEXT, -- PDF/DOCX download link
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cover_letters_user_id ON cover_letters(user_id);
CREATE INDEX idx_cover_letters_created_at ON cover_letters(created_at DESC);

-- ============================================
-- 11. JOBS & INTERNSHIPS
-- ============================================

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Job Details
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_logo_url TEXT,
    location VARCHAR(255),
    job_type VARCHAR(50), -- full-time, internship, contract
    work_mode VARCHAR(50), -- remote, hybrid, onsite
    
    -- Description
    description TEXT NOT NULL,
    requirements TEXT[],
    responsibilities TEXT[],
    skills_required TEXT[],
    
    -- Compensation
    salary_min INTEGER,
    salary_max INTEGER,
    currency VARCHAR(10) DEFAULT 'INR',
    
    -- Experience
    experience_min INTEGER, -- years
    experience_max INTEGER,
    
    -- Links
    apply_url TEXT NOT NULL,
    
    -- Metadata
    posted_date DATE,
    deadline DATE,
    source VARCHAR(50), -- linkedin, naukri, internshala, manual
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_company_name ON jobs(company_name);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_is_active ON jobs(is_active);

-- Full-text search index
CREATE INDEX idx_jobs_title_search ON jobs USING gin(to_tsvector('english', title));

-- ============================================
-- 12. JOB BOOKMARKS
-- ============================================

CREATE TABLE job_bookmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, job_id)
);

CREATE INDEX idx_job_bookmarks_user_id ON job_bookmarks(user_id);
CREATE INDEX idx_job_bookmarks_job_id ON job_bookmarks(job_id);

-- ============================================
-- 13. JOB APPLICATIONS (User Tracking)
-- ============================================

CREATE TABLE job_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    
    -- Application Details
    applied_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'applied', -- applied, screening, interview, offer, rejected
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, job_id)
);

CREATE INDEX idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX idx_job_applications_status ON job_applications(status);

-- ============================================
-- 14. JOB ALERTS
-- ============================================

CREATE TABLE job_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Alert Criteria
    keywords TEXT[], -- ["React", "Frontend"]
    locations TEXT[],
    job_types TEXT[], -- ["full-time", "internship"]
    min_salary INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    frequency VARCHAR(20) DEFAULT 'daily', -- daily, weekly, instant
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_job_alerts_user_id ON job_alerts(user_id);

-- ============================================
-- 15. COMPANIES (For Prep Packs)
-- ============================================

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name VARCHAR(255) NOT NULL UNIQUE,
    logo_url TEXT,
    description TEXT,
    website_url VARCHAR(255),
    
    -- Prep Pack Data
    interview_process JSONB, -- Rounds description
    culture_notes TEXT,
    salary_range JSONB, -- Role-wise salary data
    
    -- Questions Bank
    has_prep_pack BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_name ON companies(name);

-- ============================================
-- 16. COMPANY QUESTIONS
-- ============================================

CREATE TABLE company_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Question Details
    question_text TEXT NOT NULL,
    question_type VARCHAR(50), -- coding, system_design, hr, behavioral
    difficulty VARCHAR(20), -- easy, medium, hard
    category VARCHAR(100), -- arrays, dp, react, databases
    
    -- Solution
    solution TEXT,
    hints TEXT[],
    
    -- Metadata
    frequency VARCHAR(20), -- very_common, common, rare
    asked_in_round VARCHAR(50), -- phone_screen, onsite, final
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_company_questions_company_id ON company_questions(company_id);
CREATE INDEX idx_company_questions_type ON company_questions(question_type);

-- ============================================
-- 17. USER COMPANY PROGRESS
-- ============================================

CREATE TABLE user_company_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    completed_questions UUID[], -- Array of question IDs
    notes TEXT,
    overall_progress INTEGER DEFAULT 0, -- 0-100%
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, company_id)
);

CREATE INDEX idx_user_company_progress_user_id ON user_company_progress(user_id);

-- ============================================
-- 18. NOTIFICATIONS
-- ============================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification Content
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50), -- job_alert, roadmap_reminder, interview_reminder, achievement
    
    -- Link/Action
    action_url TEXT,
    action_text VARCHAR(100),
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- ============================================
-- 19. USER ANALYTICS
-- ============================================

CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Placement Readiness Score (0-100)
    placement_readiness_score INTEGER,
    
    -- Skill Breakdown
    dsa_score INTEGER,
    projects_score INTEGER,
    interview_score INTEGER,
    soft_skills_score INTEGER,
    resume_score INTEGER,
    
    -- Progress Metrics
    total_dsa_solved INTEGER DEFAULT 0,
    total_interviews_attended INTEGER DEFAULT 0,
    avg_interview_score DECIMAL(5,2),
    total_projects_completed INTEGER DEFAULT 0,
    
    -- Weak Areas (AI-identified)
    weak_areas TEXT[],
    
    -- Last calculated
    calculated_at TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id)
);

CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);

-- ============================================
-- 20. FEEDBACK & SUPPORT
-- ============================================

CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    type VARCHAR(50), -- bug, feature_request, general, complaint
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, resolved, closed
    admin_response TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_status ON feedback(status);

-- ============================================
-- 21. REFRESH TOKENS (for JWT)
-- ============================================

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at BEFORE UPDATE ON interviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roadmaps_updated_at BEFORE UPDATE ON career_roadmaps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skill_progress_updated_at BEFORE UPDATE ON skill_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cover_letters_updated_at BEFORE UPDATE ON cover_letters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_applications_updated_at BEFORE UPDATE ON job_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_analytics_updated_at BEFORE UPDATE ON user_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS) - Supabase Feature
-- ============================================

-- Enable RLS on user-specific tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE cover_letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_analytics ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only access their own data
CREATE POLICY users_policy ON users
    FOR ALL USING (auth.uid()::text = id::text);

CREATE POLICY resumes_policy ON resumes
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY interviews_policy ON interviews
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY interview_results_policy ON interview_results
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY roadmaps_policy ON career_roadmaps
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY skill_progress_policy ON skill_progress
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY projects_policy ON projects
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY cover_letters_policy ON cover_letters
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY job_bookmarks_policy ON job_bookmarks
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY job_applications_policy ON job_applications
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY notifications_policy ON notifications
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY user_analytics_policy ON user_analytics
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Public read access for jobs and companies
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_questions ENABLE ROW LEVEL SECURITY;

CREATE POLICY jobs_read_policy ON jobs
    FOR SELECT USING (true);

CREATE POLICY companies_read_policy ON companies
    FOR SELECT USING (true);

CREATE POLICY company_questions_read_policy ON company_questions
    FOR SELECT USING (true);

-- ============================================
-- INITIAL DATA (Optional)
-- ============================================

-- Insert some sample companies
INSERT INTO companies (name, logo_url, description, has_prep_pack) VALUES
('Google', 'https://logo.clearbit.com/google.com', 'Leading tech company', true),
('Amazon', 'https://logo.clearbit.com/amazon.com', 'E-commerce and cloud giant', true),
('Microsoft', 'https://logo.clearbit.com/microsoft.com', 'Software and cloud services', true),
('Meta', 'https://logo.clearbit.com/meta.com', 'Social media and metaverse', true),
('Netflix', 'https://logo.clearbit.com/netflix.com', 'Streaming entertainment', true),
('Apple', 'https://logo.clearbit.com/apple.com', 'Consumer electronics', true);

-- ============================================
-- VIEWS (For Complex Queries)
-- ============================================

-- User Dashboard Summary View
CREATE OR REPLACE VIEW user_dashboard_summary AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.target_role,
    ua.placement_readiness_score,
    ua.dsa_score,
    ua.projects_score,
    ua.interview_score,
    COUNT(DISTINCT ir.id) as total_interviews,
    AVG(ir.overall_score) as avg_interview_score,
    COUNT(DISTINCT p.id) as total_projects,
    (SELECT ats_score FROM resumes WHERE user_id = u.id AND is_primary = true LIMIT 1) as resume_score,
    cr.overall_progress as roadmap_progress
FROM users u
LEFT JOIN user_analytics ua ON u.id = ua.user_id
LEFT JOIN interview_results ir ON u.id = ir.user_id
LEFT JOIN projects p ON u.id = p.user_id AND p.status = 'completed'
LEFT JOIN career_roadmaps cr ON u.id = cr.user_id AND cr.is_active = true
GROUP BY u.id, u.full_name, u.target_role, ua.placement_readiness_score, 
         ua.dsa_score, ua.projects_score, ua.interview_score, cr.overall_progress;

-- Interview Performance Trend View
CREATE OR REPLACE VIEW interview_performance_trend AS
SELECT 
    user_id,
    DATE_TRUNC('week', ir.created_at) as week,
    COUNT(*) as interviews_count,
    AVG(overall_score) as avg_score,
    MAX(overall_score) as best_score
FROM interview_results ir
GROUP BY user_id, DATE_TRUNC('week', ir.created_at)
ORDER BY week DESC;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

SELECT 'PrepMind Database Schema Created Successfully!' as message;
