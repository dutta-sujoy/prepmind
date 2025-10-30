import { useState, useRef, useEffect } from 'react';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Download,
  Eye,
  Trash2,
  ArrowLeft,
  Sparkles,
  Target,
  Award,
  Star,
  MoreVertical,
  RefreshCw,
  Plus,
} from 'lucide-react';
import { resumeAPI } from '../services/api';
import './ResumeAnalyzerPage.css';

interface Resume {
  id: string;
  file_name: string;
  file_type: string;
  is_primary: boolean;
  ats_score: number | null;
  created_at: string;
}

interface ResumeAnalysis {
  ats_score: number;
  overall_rating: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  keywords: string[];
  missing_sections: string[];
  recommendations: string[];
  detailed_feedback: string;
  skills_analysis?: {
    technical_skills: string[];
    soft_skills: string[];
    missing_skills: string[];
    skill_level: string;
    skill_strength?: string;
  };
  experience_analysis?: {
    total_years: number;
    relevant_experience: boolean;
    career_progression: string;
    has_quantifiable_results?: boolean;
    gaps?: string[];
    impact_score?: string;
  };
  education_analysis?: {
    relevance: string;
    completeness: boolean;
    recommendations: string[];
    needs_improvement?: boolean;
  };
  content_quality?: {
    has_action_verbs: boolean;
    has_quantifiable_achievements: boolean;
    formatting_score: number;
    readability: string;
    keyword_density: string;
  };
  keyword_match?: {
    matched_keywords: string[];
    missing_keywords: string[];
    match_percentage: number;
  };
}

const ResumeAnalyzerPage = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // State management
  const [view, setView] = useState<'dashboard' | 'upload' | 'analysis'>('dashboard');
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [error, setError] = useState('');
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  // Load all resumes
  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      setLoading(true);
      const response = await resumeAPI.list();
      setResumes(response.data);
    } catch (err: any) {
      console.error('Error loading resumes:', err);
      setError('Failed to load resumes');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }
      if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(selectedFile.type)) {
        setError('Only PDF and DOCX files are supported');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const event = { target: { files: [droppedFile] } } as any;
      handleFileSelect(event);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      await resumeAPI.upload(file, false, true, targetRole);
      await loadResumes();
      setView('dashboard');
      setFile(null);
      setTargetRole('Software Engineer');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload resume. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (resumeId: string) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    
    try {
      await resumeAPI.delete(resumeId);
      await loadResumes();
      setActiveMenu(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete resume');
    }
  };

  const handleSetPrimary = async (resumeId: string) => {
    try {
      await resumeAPI.setPrimary(resumeId);
      await loadResumes();
      setActiveMenu(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to set as primary');
    }
  };

  const handleDownload = async (resumeId: string) => {
    try {
      const response = await resumeAPI.download(resumeId);
      window.open(response.data.download_url, '_blank');
      setActiveMenu(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download resume');
    }
  };

  const handleViewAnalysis = async (resumeId: string) => {
    try {
      setLoadingAnalysis(true);
      setSelectedResumeId(resumeId);
      setError('');
      
      const response = await resumeAPI.getAnalysis(resumeId);
      
      console.log('Analysis response:', response.data); // Debug log
      
      // The backend returns nested analysis data: { resume_id, file_name, analysis: {...}, ats_score, analyzed_at }
      const responseData = response.data;
      const analysisData = responseData.analysis || responseData;
      
      // Check if analysis data exists
      if (!analysisData || Object.keys(analysisData).length === 0) {
        setError('No analysis found for this resume. Please analyze it first.');
        setLoadingAnalysis(false);
        return;
      }
      
      // Transform backend response to match our interface
      const formattedAnalysis: ResumeAnalysis = {
        ats_score: analysisData.ats_score || responseData.ats_score || 0,
        overall_rating: analysisData.overall_rating || 'average',
        strengths: analysisData.strengths || [],
        weaknesses: analysisData.weaknesses || [],
        suggestions: analysisData.suggestions || analysisData.recommendations || [],
        keywords: analysisData.keywords || [],
        missing_sections: analysisData.missing_sections || [],
        recommendations: analysisData.recommendations || [],
        detailed_feedback: analysisData.detailed_feedback || '',
        skills_analysis: analysisData.skills_analysis,
        experience_analysis: analysisData.experience_analysis,
        education_analysis: analysisData.education_analysis,
        content_quality: analysisData.content_quality,
        keyword_match: analysisData.keyword_match
      };
      
      console.log('Formatted analysis:', formattedAnalysis); // Debug log
      
      setAnalysis(formattedAnalysis);
      setView('analysis');
      setActiveMenu(null);
    } catch (err: any) {
      console.error('Error loading analysis:', err);
      setError(err.response?.data?.detail || 'Failed to load analysis. Make sure the resume has been analyzed.');
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const handleReanalyze = async (resumeId: string) => {
    try {
      await resumeAPI.analyze(resumeId, targetRole);
      await loadResumes();
      setActiveMenu(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to re-analyze resume');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getScoreColor = (score: number | null) => {
    if (!score) return '#94a3b8';
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  // Dashboard View - List all resumes
  const renderDashboard = () => (
    <div className="resume-content">
      {loadingAnalysis && (
        <div className="loading-overlay">
          <div className="loading-modal">
            <div className="spinner"></div>
            <p>Loading analysis...</p>
          </div>
        </div>
      )}

      <div className="page-header">
        <div className="page-title">
          <h1>Resume Analyzer</h1>
          <p>Manage and analyze your resumes with AI</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={loadResumes} disabled={loading}>
            <RefreshCw size={18} />
            Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setView('upload')}>
            <Plus size={20} />
            Upload Resume
          </button>
        </div>
      </div>

      <div className="resume-dashboard">

        {error && (
          <div className="error-banner">
            <AlertCircle size={20} />
            <span>{error}</span>
            <button onClick={() => setError('')}>×</button>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <div className="empty-state">
            <FileText size={48} color="#94a3b8" />
            <h3>No Resumes Yet</h3>
            <p>Upload your first resume to get started with AI-powered analysis</p>
            <button className="btn btn-primary btn-large" onClick={() => setView('upload')}>
              <Upload size={20} />
              Upload Resume
            </button>
          </div>
        ) : (
          <div className="resumes-grid">
            {resumes.map((resume) => (
              <div key={resume.id} className={`resume-card ${resume.is_primary ? 'primary' : ''}`}>
                {resume.is_primary && (
                  <div className="primary-badge">
                    <Star size={14} fill="#fbbf24" color="white" />
                    Primary
                  </div>
                )}

                <div className="resume-card-header">
                  <div className="file-icon">
                    <FileText size={24} color="#3b82f6" />
                  </div>
                  <button 
                    className="menu-button"
                    onClick={() => setActiveMenu(activeMenu === resume.id ? null : resume.id)}
                  >
                    <MoreVertical size={20} />
                  </button>

                  {activeMenu === resume.id && (
                    <div className="dropdown-menu">
                      {resume.ats_score && (
                        <button onClick={() => handleViewAnalysis(resume.id)}>
                          <Eye size={16} />
                          View Analysis
                        </button>
                      )}
                      <button onClick={() => handleReanalyze(resume.id)}>
                        <RefreshCw size={16} />
                        Re-analyze
                      </button>
                      <button onClick={() => handleDownload(resume.id)}>
                        <Download size={16} />
                        Download
                      </button>
                      {!resume.is_primary && (
                        <button onClick={() => handleSetPrimary(resume.id)}>
                          <Star size={16} />
                          Set as Primary
                        </button>
                      )}
                      <button className="danger" onClick={() => handleDelete(resume.id)}>
                        <Trash2 size={16} />
                        Delete
                      </button>
                    </div>
                  )}
                </div>

                <div className="resume-card-body">
                  <h3 className="resume-name">{resume.file_name}</h3>
                  <div className="resume-meta">
                    <span className="file-type">{resume.file_type.toUpperCase()}</span>
                    <span className="upload-date">{formatDate(resume.created_at)}</span>
                  </div>

                  {resume.ats_score !== null ? (
                    <div className="ats-score-container">
                      <div className="score-circle" style={{ borderColor: getScoreColor(resume.ats_score) }}>
                        <span className="score-value" style={{ color: getScoreColor(resume.ats_score) }}>
                          {resume.ats_score}
                        </span>
                        
                      </div>
                      <div className="score-status">
                        <span>ATS Score</span>
                        <p className="score-desc">
                          {resume.ats_score >= 80 ? 'Excellent' : 
                           resume.ats_score >= 60 ? 'Good' : 'Needs Improvement'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="no-analysis">
                      <AlertCircle size={20} color="#94a3b8" />
                      <span>Not analyzed yet</span>
                    </div>
                  )}
                </div>

                <div className="resume-card-footer">
                  {resume.ats_score ? (
                    <button 
                      className="btn btn-primary btn-small"
                      onClick={() => handleViewAnalysis(resume.id)}
                    >
                      <Eye size={16} />
                      View Analysis
                    </button>
                  ) : (
                    <button 
                      className="btn btn-secondary btn-small"
                      onClick={() => handleReanalyze(resume.id)}
                    >
                      <Sparkles size={16} />
                      Analyze Now
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  // Upload View
  const renderUpload = () => (
    <div className="resume-content">
      <div className="resume-upload-section">
        <button className="back-button-inline" onClick={() => setView('dashboard')}>
          <ArrowLeft size={20} />
          Back to Resumes
        </button>
        <div className="upload-container">
          <div className="upload-header">
            <h1>Upload New Resume</h1>
            <p>Upload your resume and get personalized AI-powered feedback</p>
          </div>

          <div className="upload-form">
            <div className="target-role-input">
              <label htmlFor="targetRole">Target Role (optional)</label>
              <input
                type="text"
                id="targetRole"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g., Software Engineer, Data Scientist"
              />
            </div>

            {!file ? (
              <div
                className="upload-dropzone"
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="dropzone-icon">
                  <Upload size={40} />
                </div>
                <h3>Drag & drop your resume here</h3>
                <p>or click to browse files</p>
                <p className="file-info">Supports PDF, DOCX (Max 5MB)</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>
            ) : (
              <div className="file-preview">
                <div className="file-info-card">
                  <FileText size={36} color="#3b82f6" />
                  <div className="file-details">
                    <h4>{file.name}</h4>
                    <p>{(file.size / 1024).toFixed(2)} KB</p>
                  </div>
                  <button className="delete-btn" onClick={() => setFile(null)}>
                    <Trash2 size={20} />
                  </button>
                </div>

                {error && (
                  <div className="error-message">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                  </div>
                )}

                <button
                  className="btn btn-primary btn-large"
                  onClick={handleUpload}
                  disabled={uploading}
                >
                  {uploading ? 'Uploading...' : 'Upload & Analyze'}
                </button>
              </div>
            )}
          </div>

          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">
                <TrendingUp size={20} />
              </div>
              <h4>ATS Score</h4>
              <p>Get instant ATS compatibility scoring</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <Sparkles size={20} />
              </div>
              <h4>AI Feedback</h4>
              <p>Personalized suggestions from AI</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <Target size={20} />
              </div>
              <h4>Keywords</h4>
              <p>Optimize for your target role</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Analysis View
  const renderAnalysis = () => {
    if (!analysis) return null;

    return (
      <div className="resume-content">
        <div className="resume-analysis-content">
          <button className="back-button-inline" onClick={() => setView('dashboard')}>
            <ArrowLeft size={20} />
            Back to Resumes
          </button>
          <div className="analysis-container">
            <div className="analysis-hero">
              <div className="score-showcase">
                <div className="score-circle-xl">
                  <svg viewBox="0 0 200 200">
                    <circle cx="100" cy="100" r="90" fill="none" stroke="#e2e8f0" strokeWidth="20" />
                    <circle
                      cx="100"
                      cy="100"
                      r="90"
                      fill="none"
                      stroke={getScoreColor(analysis.ats_score)}
                      strokeWidth="20"
                      strokeDasharray="565.5"
                      strokeDashoffset={565.5 - (565.5 * analysis.ats_score) / 100}
                      strokeLinecap="round"
                      transform="rotate(-90 100 100)"
                    />
                  </svg>
                  <div className="score-text">
                    <span className="score-number">{analysis.ats_score}</span>
                    <span className="score-label">ATS Score</span>
                  </div>
                </div>
                <div className="score-status">
                  <Award size={24} color={getScoreColor(analysis.ats_score)} />
                  <h2>
                    {analysis.ats_score >= 80 ? 'Great Resume!' : 
                     analysis.ats_score >= 60 ? 'Good Resume!' : 'Needs Improvement'}
                  </h2>
                  <p>Your resume is {analysis.ats_score >= 80 ? 'well-optimized' : analysis.ats_score >= 60 ? 'moderately optimized' : 'not well-optimized'} for ATS systems</p>
                </div>
              </div>
            </div>

            <div className="analysis-grid">
              <div className="analysis-card strengths-card">
                <div className="card-header">
                  <CheckCircle size={18} color="#10b981" />
                  <h3>Strengths</h3>
                </div>
                <ul className="analysis-list">
                  {analysis.strengths.map((strength, idx) => (
                    <li key={idx}>{strength}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-card weaknesses-card">
                <div className="card-header">
                  <AlertCircle size={18} color="#f59e0b" />
                  <h3>Areas to Improve</h3>
                </div>
                <ul className="analysis-list">
                  {analysis.weaknesses.map((weakness, idx) => (
                    <li key={idx}>{weakness}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-card suggestions-card">
                <div className="card-header">
                  <Sparkles size={18} color="#3b82f6" />
                  <h3>AI Suggestions</h3>
                </div>
                <ul className="analysis-list">
                  {(analysis.suggestions && analysis.suggestions.length > 0 
                    ? analysis.suggestions 
                    : analysis.recommendations || []
                  ).map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-card keywords-card">
                <div className="card-header">
                  <Target size={18} color="#8b5cf6" />
                  <h3>Detected Keywords</h3>
                </div>
                {analysis.keywords && analysis.keywords.length > 0 ? (
                  <div className="keywords-grid">
                    {analysis.keywords.map((keyword, idx) => (
                      <span key={idx} className="keyword-badge">{keyword}</span>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    No keywords detected
                  </p>
                )}
                {analysis.missing_sections && analysis.missing_sections.length > 0 && (
                  <div className="missing-sections">
                    <h4>Missing Sections:</h4>
                    <div className="keywords-grid">
                      {analysis.missing_sections.map((section, idx) => (
                        <span key={idx} className="keyword-badge missing">{section}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Detailed Feedback Section */}
            {analysis.detailed_feedback && (
              <div className="detailed-scores">
                <h3>Detailed AI Feedback</h3>
                <div style={{ 
                  padding: '1rem', 
                  background: 'var(--surface)', 
                  borderRadius: '0.65rem',
                  lineHeight: '1.6',
                  fontSize: '0.875rem',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'pre-line'
                }}>
                  {analysis.detailed_feedback}
                </div>
              </div>
            )}

            {/* Skills & Experience Analysis */}
            <div className="detailed-scores">
              <h3>Detailed Breakdown</h3>
              <div className="scores-grid">
                {/* Content Quality */}
                {analysis.content_quality && (
                  <div className="score-metric">
                    <div className="metric-header">
                      <span className="metric-name">Content Quality</span>
                      <span className="metric-value">{analysis.content_quality.formatting_score || 70}%</span>
                    </div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ width: `${analysis.content_quality.formatting_score || 70}%` }}></div>
                    </div>
                    <p className="metric-desc">
                      {analysis.content_quality.has_action_verbs ? '✓ Has action verbs' : '✗ Missing action verbs'}
                      {' • '}
                      {analysis.content_quality.has_quantifiable_achievements ? '✓ Quantifiable results' : '✗ Add metrics'}
                    </p>
                  </div>
                )}

                {/* Skills Assessment */}
                {analysis.skills_analysis && (
                  <div className="score-metric">
                    <div className="metric-header">
                      <span className="metric-name">Skills Profile</span>
                      <span className="metric-value">
                        {analysis.skills_analysis.skill_level?.toUpperCase() || 'MID'}
                      </span>
                    </div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ 
                        width: analysis.skills_analysis.skill_strength === 'strong' ? '85%' : 
                               analysis.skills_analysis.skill_strength === 'moderate' ? '65%' : '45%'
                      }}></div>
                    </div>
                    <p className="metric-desc">
                      {analysis.skills_analysis.technical_skills?.length || 0} technical skills • 
                      {' '}{analysis.skills_analysis.soft_skills?.length || 0} soft skills
                    </p>
                  </div>
                )}

                {/* Keyword Match */}
                {analysis.keyword_match && (
                  <div className="score-metric">
                    <div className="metric-header">
                      <span className="metric-name">Keyword Match</span>
                      <span className="metric-value">{analysis.keyword_match.match_percentage || 50}%</span>
                    </div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ width: `${analysis.keyword_match.match_percentage || 50}%` }}></div>
                    </div>
                    <p className="metric-desc">
                      {analysis.keyword_match.matched_keywords?.length || 0} matched keywords • 
                      {' '}{analysis.keyword_match.missing_keywords?.length || 0} missing
                    </p>
                  </div>
                )}

                {/* Experience Quality */}
                {analysis.experience_analysis && (
                  <div className="score-metric">
                    <div className="metric-header">
                      <span className="metric-name">Experience Quality</span>
                      <span className="metric-value">
                        {analysis.experience_analysis.career_progression?.toUpperCase() || 'AVERAGE'}
                      </span>
                    </div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ 
                        width: analysis.experience_analysis.career_progression === 'excellent' ? '90%' : 
                               analysis.experience_analysis.career_progression === 'good' ? '75%' : '60%'
                      }}></div>
                    </div>
                    <p className="metric-desc">
                      {analysis.experience_analysis.total_years || 0} years experience • 
                      {' '}{analysis.experience_analysis.impact_score || 'medium'} impact
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="action-buttons">
              <button className="btn btn-secondary btn-large" onClick={() => handleDownload(selectedResumeId!)}>
                <Download size={20} />
                Download Report
              </button>
              <button className="btn btn-primary btn-large" onClick={() => setView('dashboard')}>
                Back to Resumes
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Main Render
  return (
    <>
      {view === 'dashboard' && renderDashboard()}
      {view === 'upload' && renderUpload()}
      {view === 'analysis' && renderAnalysis()}
    </>
  );
};

export default ResumeAnalyzerPage;

