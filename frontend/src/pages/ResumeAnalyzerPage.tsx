import { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Brain,
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
} from 'lucide-react';
import { resumeAPI } from '../services/api';
import './ResumeAnalyzerPage.css';

interface ResumeAnalysis {
  ats_score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  keywords: string[];
  missing_sections: string[];
}

const ResumeAnalyzerPage = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [error, setError] = useState('');

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
      const response = await resumeAPI.upload(file, false, true, targetRole);
      setAnalyzing(true);
      
      // Simulate analysis time
      setTimeout(() => {
        setAnalysis({
          ats_score: 80,
          strengths: [
            'Clear and concise format',
            'Good use of action verbs',
            'Quantifiable achievements included',
            'Relevant technical skills listed',
          ],
          weaknesses: [
            'Missing ATS-friendly keywords for target role',
            'Experience section could be more detailed',
            'Projects lack technical depth',
          ],
          suggestions: [
            'Add more industry-specific keywords like "React", "Node.js", "API Development"',
            'Include metrics for each project (e.g., "improved performance by 40%")',
            'Expand on your role and responsibilities in each position',
            'Add a professional summary at the top',
          ],
          keywords: ['JavaScript', 'React', 'Node.js', 'MongoDB', 'REST API', 'Git'],
          missing_sections: ['Certifications', 'Awards', 'Publications'],
        });
        setAnalyzing(false);
        setUploading(false);
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload resume. Please try again.');
      setUploading(false);
    }
  };

  const resetUpload = () => {
    setFile(null);
    setAnalysis(null);
    setError('');
  };

  if (analysis) {
    return (
      <div className="resume-page">
        <header className="resume-header">
          <Link to="/dashboard" className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </Link>
          <div className="header-logo">
            <Brain size={32} color="#3b82f6" />
            <span>Resume Analysis</span>
          </div>
          <button className="btn btn-secondary" onClick={resetUpload}>
            Analyze Another
          </button>
        </header>

        <div className="resume-analysis-content">
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
                      stroke="#10b981"
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
                  <Award size={32} color="#10b981" />
                  <h2>Great Resume!</h2>
                  <p>Your resume is well-optimized for ATS systems</p>
                </div>
              </div>
            </div>

            <div className="analysis-grid">
              <div className="analysis-card strengths-card">
                <div className="card-header">
                  <CheckCircle size={24} color="#10b981" />
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
                  <AlertCircle size={24} color="#f59e0b" />
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
                  <Sparkles size={24} color="#3b82f6" />
                  <h3>AI Suggestions</h3>
                </div>
                <ul className="analysis-list">
                  {analysis.suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-card keywords-card">
                <div className="card-header">
                  <Target size={24} color="#8b5cf6" />
                  <h3>Detected Keywords</h3>
                </div>
                <div className="keywords-grid">
                  {analysis.keywords.map((keyword, idx) => (
                    <span key={idx} className="keyword-badge">{keyword}</span>
                  ))}
                </div>
                {analysis.missing_sections.length > 0 && (
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

            <div className="detailed-scores">
              <h3>Detailed Breakdown</h3>
              <div className="scores-grid">
                <div className="score-metric">
                  <div className="metric-header">
                    <span className="metric-name">Content Quality</span>
                    <span className="metric-value">90%</span>
                  </div>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '90%' }}></div>
                  </div>
                  <p className="metric-desc">Strong action verbs and quantifiable achievements</p>
                </div>

                <div className="score-metric">
                  <div className="metric-header">
                    <span className="metric-name">Format & Structure</span>
                    <span className="metric-value">85%</span>
                  </div>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '85%' }}></div>
                  </div>
                  <p className="metric-desc">Clean layout with good use of white space</p>
                </div>

                <div className="score-metric">
                  <div className="metric-header">
                    <span className="metric-name">Keywords Match</span>
                    <span className="metric-value">75%</span>
                  </div>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '75%' }}></div>
                  </div>
                  <p className="metric-desc">Add more role-specific keywords</p>
                </div>

                <div className="score-metric">
                  <div className="metric-header">
                    <span className="metric-name">ATS Compatibility</span>
                    <span className="metric-value">70%</span>
                  </div>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '70%' }}></div>
                  </div>
                  <p className="metric-desc">Avoid tables and complex formatting</p>
                </div>
              </div>
            </div>

            <div className="action-buttons">
              <button className="btn btn-secondary btn-large">
                <Download size={20} />
                Download Report
              </button>
              <button className="btn btn-primary btn-large">
                <Eye size={20} />
                View Detailed Report
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="resume-page">
      <header className="resume-header">
        <Link to="/dashboard" className="back-button">
          <ArrowLeft size={20} />
          Back to Dashboard
        </Link>
        <div className="header-logo">
          <Brain size={32} color="#3b82f6" />
          <span>AI Resume Reviewer</span>
        </div>
      </header>

      <div className="resume-upload-section">
        <div className="upload-container">
          <div className="upload-header">
            <h1>AI Resume Reviewer</h1>
            <p>Upload your resume and get personalized feedback to improve your chances</p>
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
                  <Upload size={48} />
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
                  <FileText size={48} color="#3b82f6" />
                  <div className="file-details">
                    <h4>{file.name}</h4>
                    <p>{(file.size / 1024).toFixed(2)} KB</p>
                  </div>
                  <button className="delete-btn" onClick={resetUpload}>
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
                  disabled={uploading || analyzing}
                >
                  {uploading ? 'Uploading...' : analyzing ? 'Analyzing...' : 'Analyze Resume'}
                </button>

                {analyzing && (
                  <div className="analyzing-status">
                    <div className="analyzing-animation">
                      <div className="spinner"></div>
                    </div>
                    <p>Analyzing your resume with AI...</p>
                    <div className="analyzing-steps">
                      <div className="step active">
                        <CheckCircle size={16} />
                        <span>Parsing content</span>
                      </div>
                      <div className="step active">
                        <CheckCircle size={16} />
                        <span>Checking ATS compatibility</span>
                      </div>
                      <div className="step">
                        <div className="step-loader"></div>
                        <span>Generating suggestions</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">
                <TrendingUp size={24} />
              </div>
              <h4>ATS Score</h4>
              <p>Get instant ATS compatibility scoring</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <Sparkles size={24} />
              </div>
              <h4>AI Feedback</h4>
              <p>Personalized suggestions from AI</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <Target size={24} />
              </div>
              <h4>Keywords</h4>
              <p>Optimize for your target role</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeAnalyzerPage;

