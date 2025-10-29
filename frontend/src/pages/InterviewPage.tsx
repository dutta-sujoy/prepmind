import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Brain,
  Mic,
  MicOff,
  Video,
  VideoOff,
  Settings,
  ArrowLeft,
  Play,
  Pause,
  SkipForward,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
} from 'lucide-react';
import { interviewAPI } from '../services/api';
import './InterviewPage.css';

interface Interview {
  id: string;
  interview_type: string;
  target_role: string;
  technologies: string[];
  difficulty: string;
  num_questions: number;
  questions: any[];
  status: string;
}

const InterviewPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<'setup' | 'interview' | 'result'>('setup');
  const [interview, setInterview] = useState<Interview | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [videoEnabled, setVideoEnabled] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [answer, setAnswer] = useState('');
  const [timeLeft, setTimeLeft] = useState(120); // 2 minutes per question
  const [loading, setLoading] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Setup form state
  const [setupForm, setSetupForm] = useState({
    interview_type: 'technical',
    target_role: 'Software Engineer',
    technologies: ['JavaScript', 'React'],
    difficulty: 'medium',
    num_questions: 5,
  });

  useEffect(() => {
    if (step === 'interview' && isRecording) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleNext();
            return 120;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [step, isRecording, currentQuestion]);

  const handleSetupChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setSetupForm({ ...setupForm, [name]: value });
  };

  const handleTechChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const techs = e.target.value.split(',').map((t) => t.trim());
    setSetupForm({ ...setupForm, technologies: techs });
  };

  const startInterview = async () => {
    setLoading(true);
    try {
      const response = await interviewAPI.create({
        ...setupForm,
        num_questions: parseInt(setupForm.num_questions.toString()),
      });
      setInterview(response.data);
      setStep('interview');
      startMediaRecording();
    } catch (error) {
      console.error('Failed to create interview:', error);
      alert('Failed to start interview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startMediaRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoEnabled,
        audio: audioEnabled,
      });

      if (videoRef.current && videoEnabled) {
        videoRef.current.srcObject = stream;
      }

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        // Handle recorded data
        console.log('Recorded data:', event.data);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopMediaRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleNext = () => {
    if (!interview) return;

    if (currentQuestion < interview.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setAnswer('');
      setTimeLeft(120);
    } else {
      endInterview();
    }
  };

  const endInterview = () => {
    stopMediaRecording();
    setStep('result');
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (step === 'setup') {
    return (
      <div className="interview-page">
        <header className="interview-header">
          <Link to="/dashboard" className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </Link>
          <div className="header-logo">
            <Brain size={32} color="#3b82f6" />
            <span>PrepMind Interview</span>
          </div>
        </header>

        <div className="interview-setup">
          <div className="setup-container">
            <div className="setup-header">
              <h1>Mock Interview Simulator</h1>
              <p>Practice with our AI interviewer that simulates real technical interviews</p>
            </div>

            <div className="setup-form">
              <div className="form-group">
                <label htmlFor="interview_type">Interview Type</label>
                <select
                  id="interview_type"
                  name="interview_type"
                  value={setupForm.interview_type}
                  onChange={handleSetupChange}
                >
                  <option value="technical">Technical</option>
                  <option value="hr">HR</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="target_role">Target Role</label>
                <input
                  type="text"
                  id="target_role"
                  name="target_role"
                  value={setupForm.target_role}
                  onChange={handleSetupChange}
                  placeholder="e.g., Software Engineer, Frontend Developer"
                />
              </div>

              <div className="form-group">
                <label htmlFor="technologies">Technologies (comma separated)</label>
                <input
                  type="text"
                  id="technologies"
                  value={setupForm.technologies.join(', ')}
                  onChange={handleTechChange}
                  placeholder="e.g., JavaScript, React, Node.js"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="difficulty">Difficulty</label>
                  <select
                    id="difficulty"
                    name="difficulty"
                    value={setupForm.difficulty}
                    onChange={handleSetupChange}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="num_questions">Number of Questions</label>
                  <select
                    id="num_questions"
                    name="num_questions"
                    value={setupForm.num_questions}
                    onChange={handleSetupChange}
                  >
                    <option value="3">3 Questions</option>
                    <option value="5">5 Questions</option>
                    <option value="10">10 Questions</option>
                    <option value="15">15 Questions</option>
                  </select>
                </div>
              </div>

              <div className="media-settings">
                <h3>Media Settings</h3>
                <div className="media-toggles">
                  <label className="toggle-item">
                    <input
                      type="checkbox"
                      checked={audioEnabled}
                      onChange={(e) => setAudioEnabled(e.target.checked)}
                    />
                    <Mic size={20} />
                    <span>Enable Microphone</span>
                  </label>
                  <label className="toggle-item">
                    <input
                      type="checkbox"
                      checked={videoEnabled}
                      onChange={(e) => setVideoEnabled(e.target.checked)}
                    />
                    <Video size={20} />
                    <span>Enable Camera</span>
                  </label>
                </div>
              </div>

              <button
                className="btn btn-primary btn-large"
                onClick={startInterview}
                disabled={loading}
              >
                {loading ? 'Generating Questions...' : 'Start Interview'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'interview' && interview) {
    const question = interview.questions[currentQuestion];
    const progress = ((currentQuestion + 1) / interview.questions.length) * 100;

    return (
      <div className="interview-page interview-active">
        <div className="interview-session">
          <div className="interview-video-panel">
            <div className="video-container">
              {videoEnabled ? (
                <video ref={videoRef} autoPlay muted className="user-video" />
              ) : (
                <div className="video-placeholder">
                  <Brain size={64} color="#3b82f6" />
                  <p>Camera Off</p>
                </div>
              )}
              <div className="ai-avatar">
                <div className="ai-avatar-circle">
                  <Brain size={32} color="#fff" />
                </div>
                <div className="ai-speaking-indicator">
                  {isRecording && (
                    <>
                      <span></span>
                      <span></span>
                      <span></span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="video-controls">
              <button
                className={`control-btn ${!audioEnabled ? 'disabled' : ''}`}
                onClick={() => setAudioEnabled(!audioEnabled)}
              >
                {audioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
              </button>
              <button
                className={`control-btn ${!videoEnabled ? 'disabled' : ''}`}
                onClick={() => setVideoEnabled(!videoEnabled)}
              >
                {videoEnabled ? <Video size={20} /> : <VideoOff size={20} />}
              </button>
              <button className="control-btn">
                <Settings size={20} />
              </button>
              <button className="control-btn end-call" onClick={endInterview}>
                End Interview
              </button>
            </div>
          </div>

          <div className="interview-content-panel">
            <div className="interview-header-bar">
              <div className="interview-progress">
                <span className="progress-text">
                  Question {currentQuestion + 1} of {interview.questions.length}
                </span>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>
              </div>
              <div className="interview-timer">
                <Clock size={20} />
                <span className={timeLeft < 30 ? 'time-warning' : ''}>{formatTime(timeLeft)}</span>
              </div>
            </div>

            <div className="question-panel">
              <div className="question-header">
                <h2>Current Question:</h2>
                <span className="question-category">{question?.category || 'Technical'}</span>
              </div>
              <p className="question-text">{question?.question_text || question?.text}</p>

              {question?.hints && question.hints.length > 0 && (
                <div className="question-hints">
                  <h4>Follow-up Hints:</h4>
                  <ul>
                    {question.hints.map((hint: string, idx: number) => (
                      <li key={idx}>{hint}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="answer-panel">
              <h3>Your Response</h3>
              <div className="recording-indicator">
                {isRecording && (
                  <>
                    <div className="recording-dot"></div>
                    <span>AI Voice Active</span>
                  </>
                )}
              </div>
              <textarea
                className="answer-input"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Speak clearly into your microphone. Your response is being analyzed in real-time..."
                rows={6}
              />
              <div className="answer-actions">
                <button className="btn btn-secondary" onClick={handleNext}>
                  Skip Question
                </button>
                <button className="btn btn-primary" onClick={handleNext}>
                  Next Question <SkipForward size={20} />
                </button>
              </div>
            </div>

            <div className="live-feedback">
              <h4>
                <TrendingUp size={20} />
                Live Feedback
              </h4>
              <div className="feedback-metrics">
                <div className="metric-item">
                  <span className="metric-label">Technical Accuracy</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '78%' }}></div>
                  </div>
                  <span className="metric-value">78%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Communication</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '85%' }}></div>
                  </div>
                  <span className="metric-value">85%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Confidence</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: '72%' }}></div>
                  </div>
                  <span className="metric-value">72%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'result') {
    return (
      <div className="interview-page">
        <header className="interview-header">
          <Link to="/dashboard" className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </Link>
          <div className="header-logo">
            <Brain size={32} color="#3b82f6" />
            <span>Interview Complete</span>
          </div>
        </header>

        <div className="interview-result">
          <div className="result-container">
            <div className="result-hero">
              <div className="result-icon">
                <CheckCircle size={64} color="#10b981" />
              </div>
              <h1>Interview Completed!</h1>
              <p>Great job! Here's your performance summary</p>
            </div>

            <div className="result-score">
              <div className="overall-score">
                <h2>Overall Score</h2>
                <div className="score-circle-large">
                  <svg viewBox="0 0 200 200">
                    <circle cx="100" cy="100" r="90" fill="none" stroke="#e2e8f0" strokeWidth="20" />
                    <circle
                      cx="100"
                      cy="100"
                      r="90"
                      fill="none"
                      stroke="#3b82f6"
                      strokeWidth="20"
                      strokeDasharray="565.5"
                      strokeDashoffset="141.375"
                      strokeLinecap="round"
                      transform="rotate(-90 100 100)"
                    />
                  </svg>
                  <div className="score-text">
                    <span className="score-number">75</span>
                    <span className="score-label">/ 100</span>
                  </div>
                </div>
              </div>

              <div className="score-breakdown">
                <h3>Performance Breakdown</h3>
                <div className="breakdown-items">
                  <div className="breakdown-item">
                    <span className="breakdown-label">Technical Accuracy</span>
                    <div className="breakdown-bar">
                      <div className="breakdown-fill" style={{ width: '78%' }}></div>
                    </div>
                    <span className="breakdown-value">78%</span>
                  </div>
                  <div className="breakdown-item">
                    <span className="breakdown-label">Communication</span>
                    <div className="breakdown-bar">
                      <div className="breakdown-fill" style={{ width: '85%' }}></div>
                    </div>
                    <span className="breakdown-value">85%</span>
                  </div>
                  <div className="breakdown-item">
                    <span className="breakdown-label">Problem Solving</span>
                    <div className="breakdown-bar">
                      <div className="breakdown-fill" style={{ width: '72%' }}></div>
                    </div>
                    <span className="breakdown-value">72%</span>
                  </div>
                  <div className="breakdown-item">
                    <span className="breakdown-label">Confidence</span>
                    <div className="breakdown-bar">
                      <div className="breakdown-fill" style={{ width: '68%' }}></div>
                    </div>
                    <span className="breakdown-value">68%</span>
                  </div>
                  <div className="breakdown-item">
                    <span className="breakdown-label">Completeness</span>
                    <div className="breakdown-bar">
                      <div className="breakdown-fill" style={{ width: '65%' }}></div>
                    </div>
                    <span className="breakdown-value">65%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="result-feedback-section">
              <div className="feedback-box strengths">
                <h3>
                  <CheckCircle size={24} color="#10b981" />
                  Strengths
                </h3>
                <ul>
                  <li>Good explanation of media query usage</li>
                  <li>Clear structure in your response</li>
                  <li>Excellent communication skills</li>
                </ul>
              </div>

              <div className="feedback-box improvements">
                <h3>
                  <AlertCircle size={24} color="#f59e0b" />
                  Areas for Improvement
                </h3>
                <ul>
                  <li>Consider mentioning React hooks for state management</li>
                  <li>Speak a bit slower for better clarity</li>
                  <li>Work on optimizing time complexity</li>
                </ul>
              </div>
            </div>

            <div className="result-actions">
              <button className="btn btn-secondary btn-large" onClick={() => navigate('/interview')}>
                Practice Again
              </button>
              <button className="btn btn-primary btn-large" onClick={() => navigate('/dashboard')}>
                View Detailed Report
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default InterviewPage;

