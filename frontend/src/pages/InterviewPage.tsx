import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Brain,
  Mic,
  MicOff,
  Plus,
  Play,
  Eye,
  Trash2,
  Calendar,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Award,
  Target,
  RefreshCw,
  X,
  SkipForward,
  MessageSquare,
  BarChart,
  FileText,
  User,
  Volume2,
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
  created_at: string;
  completed_at?: string;
}

interface InterviewResult {
  id: string;
  interview_id: string;
  overall_score: number;
  summary: string;
  detailed_feedback: any;
  improvement_areas: string[];
  strengths: string[];
  transcript: any[];
  created_at: string;
}

const InterviewPage = () => {
  const navigate = useNavigate();
  
  // View state
  const [view, setView] = useState<'dashboard' | 'create' | 'session' | 'result'>('dashboard');
  
  // Data state
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [selectedInterview, setSelectedInterview] = useState<Interview | null>(null);
  const [interviewResult, setInterviewResult] = useState<InterviewResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Interview session state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [timeLeft, setTimeLeft] = useState(180); // 3 minutes per question
  const [transcript, setTranscript] = useState('');
  const [answers, setAnswers] = useState<any[]>([]);
  
  // Conversational mode state
  const [interviewStyle] = useState<'conversational' | 'structured'>('conversational');
  const [chatMessages, setChatMessages] = useState<Array<{
    role: 'ai' | 'user';
    message: string;
    timestamp: Date;
    isPlaying?: boolean;
  }>>([]);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  
  // WebSocket connection
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const silenceTimeoutRef = useRef<number | null>(null);
  const isSpeakingRef = useRef(false);
  const recognitionRef = useRef<any>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const isAiSpeakingRef = useRef(false);
  
  // Create form state
  const [createForm, setCreateForm] = useState({
    interview_type: 'technical',
    target_role: 'Software Engineer',
    technologies: ['JavaScript', 'React'],
    difficulty: 'medium',
    num_questions: 5,
  });

  useEffect(() => {
    loadInterviews();
  }, []);

  useEffect(() => {
    // Timer only for structured interview mode, NOT conversational
    if (
      view === 'session' && 
      selectedInterview && 
      interviewStyle !== 'conversational' &&
      currentQuestionIndex < selectedInterview.questions.length
    ) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleNextQuestion();
            return 180;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [view, currentQuestionIndex, selectedInterview, interviewStyle]);

  const loadInterviews = async () => {
    try {
      setLoading(true);
      const response = await interviewAPI.list();
      setInterviews(response.data);
    } catch (err: any) {
      console.error('Error loading interviews:', err);
      setError('Failed to load interviews');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInterview = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await interviewAPI.create({
        ...createForm,
        technologies: createForm.technologies.filter(t => t.trim() !== ''),
      });
      setSelectedInterview(response.data);
      await loadInterviews();
      setView('dashboard');
    } catch (err: any) {
      console.error('Error creating interview:', err);
      setError(err.response?.data?.detail || 'Failed to create interview');
    } finally {
      setLoading(false);
    }
  };

  const handleStartInterview = async (interview: Interview) => {
    console.log('Starting interview:', interview);
    
    try {
      // Fetch full interview details with questions
      console.log('Fetching full interview details...');
      const response = await interviewAPI.get(interview.id);
      const fullInterview = response.data;
      console.log('Full interview loaded:', fullInterview);
      
      setSelectedInterview(fullInterview);
      setCurrentQuestionIndex(0);
      setTimeLeft(180);
      setAnswers([]);
      setTranscript('');
      setView('session');
      
      console.log('View set to session, initializing media and WebSocket...');
      
      // Initialize WebSocket connection
      initializeWebSocket(interview.id);
      
      // Start media capture after a brief delay to ensure view is rendered
      setTimeout(() => {
        startMediaCapture();
      }, 100);
    } catch (error: any) {
      console.error('Failed to load interview details:', error);
      setError(error.response?.data?.detail || 'Failed to start interview');
      return;
    }
  };

  const startMediaCapture = async () => {
    try {
      // Request both audio and video
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        },
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      });
      
      console.log('Media stream obtained:', stream);
      streamRef.current = stream;
      
      // Set video source
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(err => console.error('Video play error:', err));
      }
      
      // Set up voice activity detection
      setupVoiceActivityDetection(stream);
      
      // Create audio-only recorder for sending to backend
      const audioTrack = stream.getAudioTracks()[0];
      const audioStream = new MediaStream([audioTrack]);
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType: 'audio/webm'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        console.log('Audio data available:', event.data.size, 'bytes');
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          // Send audio chunk to WebSocket for real-time processing
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            // Convert audio blob to base64 and send as JSON message
            event.data.arrayBuffer().then(async (buffer) => {
              // Create base64 from buffer
              const base64Audio = btoa(
                new Uint8Array(buffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
              );
              console.log('Sending audio chunk, size:', base64Audio.length, 'format: audio/webm');
              wsRef.current?.send(JSON.stringify({
                type: 'audio_chunk',
                data: base64Audio,
                format: 'webm' // Explicitly send format
              }));
            });
          }
        }
      };
      
      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
      };
      
      mediaRecorder.onstart = () => {
        console.log('MediaRecorder started');
        setIsRecording(true);
      };
      
      mediaRecorder.onstop = () => {
        console.log('MediaRecorder stopped');
      };
      
      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms for real-time
      console.log('MediaRecorder start called');
      
      // Start Web Speech Recognition (browser-based transcription - NO backend needed!)
      setupWebSpeechRecognition();
      
    } catch (err) {
      console.error('Failed to access media:', err);
      setError('Please enable camera and microphone access to continue');
    }
  };

  const setupWebSpeechRecognition = () => {
    // Use browser's built-in Web Speech API (works in Chrome/Edge - NO backend needed!)
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Web Speech API not supported in this browser');
      return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Keep listening
    recognition.interimResults = true; // Show partial results
    recognition.lang = 'en-US';
    
    let finalTranscript = '';
    let interimTranscript = '';
    let isUserSpeaking = false;
    
    recognition.onresult = (event: any) => {
      // Don't process if AI is speaking (use ref for immediate check)
      if (isAiSpeakingRef.current) {
        console.log('⏸️ Ignoring recognition while AI speaks');
        return;
      }
      
      interimTranscript = '';
      let hasNewFinalResult = false;
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          hasNewFinalResult = true;
          console.log('✅ Final transcript:', transcript);
          
          // Show only this final result temporarily
          setCurrentTranscript(transcript.trim());
          
          // Add to chat messages
          setChatMessages(prev => [...prev, {
            role: 'user',
            message: transcript.trim(),
            timestamp: new Date()
          }]);
          
          // Send to backend
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
              type: 'user_message',
              message: transcript.trim()
            }));
          }
          
          // Clear caption after 2 seconds (it's been sent)
          setTimeout(() => {
            setCurrentTranscript('');
          }, 2000);
        } else {
          // Interim result - user is speaking (show only current speech)
          interimTranscript += transcript;
          setCurrentTranscript(interimTranscript.trim());
          
          // Interrupt AI if user starts speaking
          if (!isUserSpeaking && interimTranscript.length > 3) {
            isUserSpeaking = true;
            // Stop any playing AI audio
            if (currentAudioRef.current) {
              currentAudioRef.current.pause();
              currentAudioRef.current.currentTime = 0;
              currentAudioRef.current = null;
              console.log('🔇 User interrupted AI');
            }
            // Clear BOTH state and ref
            setIsAiSpeaking(false);
            isAiSpeakingRef.current = false;
          }
        }
      }
      
      if (hasNewFinalResult) {
        isUserSpeaking = false;
      }
    };
    
    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'no-speech') {
        // This is normal, just continue
        return;
      }
      if (event.error === 'aborted') {
        // Recognition was stopped, this is expected
        return;
      }
    };
    
    recognition.onend = () => {
      console.log('Speech recognition ended, isAiSpeaking:', isAiSpeaking);
      // DO NOT auto-restart - we'll manually restart after AI finishes
      // This prevents capturing AI's voice
    };
    
    recognitionRef.current = recognition;
    
    // Don't start immediately - wait for AI to finish greeting
    console.log('✅ Web Speech Recognition initialized (will start after AI greeting)');
  };

  const setupVoiceActivityDetection = (stream: MediaStream) => {
    // Create audio context for voice detection
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    audioContextRef.current = audioContext;
    
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.8;
    
    source.connect(analyser);
    analyserRef.current = analyser;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    let silenceStart = Date.now();
    let lastSoundTime = Date.now();
    const SILENCE_THRESHOLD = 30; // Volume threshold (0-255)
    const SILENCE_DURATION = 1500; // 1.5 seconds of silence to trigger audio_complete
    const MIN_SPEECH_DURATION = 800; // Minimum 0.8 seconds of speech before considering it valid
    
    const checkAudioLevel = () => {
      if (!analyserRef.current) return;
      
      analyser.getByteFrequencyData(dataArray);
      
      // Calculate average volume
      const average = dataArray.reduce((a, b) => a + b) / bufferLength;
      
      console.log('Audio level:', Math.round(average));
      
      // Detect if user is speaking
      if (average > SILENCE_THRESHOLD) {
        lastSoundTime = Date.now();
        
        if (!isSpeakingRef.current) {
          console.log('🎤 User started speaking');
          isSpeakingRef.current = true;
          silenceStart = Date.now();
          setIsRecording(true);
        }
        
        // Clear any existing silence timeout
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
          silenceTimeoutRef.current = null;
        }
      } else {
        // Silence detected
        const silenceDuration = Date.now() - lastSoundTime;
        const speechDuration = lastSoundTime - silenceStart;
        
        if (isSpeakingRef.current && silenceDuration > SILENCE_DURATION && speechDuration > MIN_SPEECH_DURATION) {
          console.log('🔇 Silence detected, sending audio_complete');
          
          // User stopped speaking
          isSpeakingRef.current = false;
          setIsRecording(false);
          
          // Signal audio complete to backend
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.log('📤 Sending audio_complete signal');
            wsRef.current.send(JSON.stringify({ 
              type: 'audio_complete'
            }));
          }
          
          // Reset for next speech
          silenceStart = Date.now();
        }
      }
      
      // Continue monitoring
      requestAnimationFrame(checkAudioLevel);
    };
    
    // Start monitoring
    checkAudioLevel();
  };

  const initializeWebSocket = (interviewId: string) => {
    // Get auth token
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Authentication required. Please login again.');
      return;
    }
    
    // Build WebSocket URL with token query parameter
    const baseWsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    // Correct path: /api/v1/ws/interview/{id}
    const wsUrl = `${baseWsUrl}/api/v1/ws/interview/${interviewId}?token=${token}&mode=voice&style=conversational`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected successfully');
      
      // Set up keep-alive ping every 30 seconds
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        } else {
          clearInterval(pingInterval);
        }
      }, 30000);
      
      // Store interval for cleanup
      (ws as any).pingInterval = pingInterval;
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data.type, data);
      
      switch (data.type) {
        case 'welcome':
          console.log('Welcome message, style:', data.style);
          if (data.style === 'conversational') {
            // Conversational mode - messages will come separately
          } else {
            console.log(data.message);
          }
          break;
        
        case 'ai_message':
          // AI's spoken message in conversational mode
          setChatMessages(prev => [...prev, {
            role: 'ai',
            message: data.message,
            timestamp: new Date()
          }]);
          setIsThinking(false);
          
          // Check if interview is complete
          if (data.is_complete) {
            console.log('Interview marked as complete by AI');
          }
          break;
        
        case 'ai_audio':
          // AI's audio in conversational mode
          if (data.data) {
            // Stop recognition while AI speaks
            if (recognitionRef.current) {
              try {
                recognitionRef.current.stop();
                console.log('⏸️ Paused recognition (AI speaking)');
              } catch (e) {
                console.log('Recognition already stopped');
              }
            }
            
            // Set BOTH state and ref
            setIsAiSpeaking(true);
            isAiSpeakingRef.current = true;
            
            playAudioResponse(data.data, () => {
              console.log('AI audio finished playing');
              
              // Clear BOTH state and ref
              setIsAiSpeaking(false);
              isAiSpeakingRef.current = false;
              
              // IMPORTANT: Manually restart recognition after AI finishes
              // This is the ONLY place recognition should restart
              if (recognitionRef.current) {
                setTimeout(() => {
                  // Double-check AI is not speaking before restarting
                  if (recognitionRef.current && !isAiSpeakingRef.current) {
                    try {
                      recognitionRef.current.start();
                      console.log('▶️ Recognition started (AI finished speaking)');
                    } catch (e) {
                      console.error('Failed to start recognition:', e);
                    }
                  } else {
                    console.log('⚠️ Skipped recognition restart (AI still speaking)');
                  }
                }, 800); // Longer delay to ensure AI audio is fully stopped
              }
            });
          }
          break;
        
        case 'thinking':
          // AI is thinking/processing
          setIsThinking(true);
          break;
        
        case 'question':
          // Question metadata received - update the UI
          console.log('Question received:', data);
          setSelectedInterview(prev => {
            if (!prev) return prev;
            // Update the current question with the received data
            const updatedQuestions = [...prev.questions];
            const questionIndex = data.question_number - 1;
            if (updatedQuestions[questionIndex]) {
              updatedQuestions[questionIndex] = {
                ...updatedQuestions[questionIndex],
                text: data.question_text,
                question_text: data.question_text,
                category: data.category,
                difficulty: data.difficulty
              };
            }
            return { ...prev, questions: updatedQuestions };
          });
          // Update current question index to match
          setCurrentQuestionIndex(data.question_number - 1);
          break;
        
        case 'generating_audio':
          // Backend is generating audio for the question
          console.log('Generating audio:', data.message);
          break;
        
        case 'question_audio':
          // Question audio received in voice mode
          if (data.data) {
            playAudioResponse(data.data);
          }
          break;
        
        case 'processing':
          // Backend is processing (transcribing/evaluating)
          console.log('Processing:', data.message);
          if (interviewStyle === 'conversational' && currentTranscript) {
            // Add user's complete message to chat
            setChatMessages(prev => [...prev, {
              role: 'user',
              message: currentTranscript,
              timestamp: new Date()
            }]);
            setCurrentTranscript(''); // Clear for next message
          }
          break;
        
        case 'transcription':
          // Real-time transcription from voice
          if (interviewStyle === 'conversational') {
            // In conversational mode, build up current transcript
            setCurrentTranscript(prev => {
              const newText = data.text;
              return prev ? `${prev} ${newText}` : newText;
            });
          } else {
            // Structured mode
            setTranscript(prev => {
              const newText = data.text;
              return prev ? `${prev} ${newText}` : newText;
            });
          }
          break;
        
        case 'evaluating':
          // Backend is evaluating the answer
          console.log('Evaluating:', data.message);
          break;
        
        case 'feedback':
          // Real-time feedback after answer
          console.log('Feedback received:', data);
          // Clear transcript for next question
          setTranscript('');
          break;
        
        case 'generating_report':
          // Backend is generating final report
          console.log('Generating report:', data.message);
          setIsThinking(true);
          setIsAiSpeaking(false);
          break;
        
        case 'interview_complete':
          // Interview finished by AI - backend has already generated the report
          console.log('Interview complete:', data);
          handleInterviewCompleteByAI();
          break;
        
        case 'error':
          // Error message from backend
          console.error('Backend error:', data.message);
          setError(data.message);
          break;
        
        case 'pong':
          // Keep-alive response
          break;
        
        default:
          console.log('Unknown message type:', data.type, data);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please try again.');
    };
    
    ws.onclose = () => {
      console.log('WebSocket connection closed');
      
      // Clear ping interval
      if ((ws as any).pingInterval) {
        clearInterval((ws as any).pingInterval);
      }
    };
    
    wsRef.current = ws;
  };

  const playAudioResponse = (audioBase64: string, onEnded?: () => void) => {
    // Stop any currently playing audio first
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
    
    // Backend sends MP3 format
    const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
    currentAudioRef.current = audio;
    
    audio.onended = () => {
      currentAudioRef.current = null;
      if (onEnded) onEnded();
    };
    
    audio.onerror = (err) => {
      console.error('Failed to play audio:', err);
      currentAudioRef.current = null;
      if (onEnded) onEnded(); // Call callback even on error
    };
    
    audio.play().catch(err => {
      console.error('Failed to play audio:', err);
      currentAudioRef.current = null;
      if (onEnded) onEnded(); // Call callback even on error
    });
  };

  const handleNextQuestion = () => {
    if (!selectedInterview) return;
    
    // Signal audio recording complete
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'audio_complete'
      }));
    }
    
    // Save current answer
    const currentAnswer = {
      question_number: currentQuestionIndex + 1,
      answer_text: transcript,
      time_taken: 180 - timeLeft,
    };
    setAnswers(prev => [...prev, currentAnswer]);
    
    // Send answer to WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'answer',
        ...currentAnswer,
      }));
    }
    
    if (currentQuestionIndex < selectedInterview.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setTranscript('');
      setTimeLeft(180);
    } else {
      handleEndInterview();
    }
  };

  const handleInterviewCompleteByAI = async () => {
    console.log('🎉 Interview completed by AI - cleaning up and fetching results...');
    setLoading(true);
    setError('');
    
    // Stop recording
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
    
    // Stop all media tracks (audio and video)
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log('Stopped track:', track.kind);
      });
      streamRef.current = null;
    }
    
    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    // Clear analyser
    analyserRef.current = null;
    
    // Clear silence timeout
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }
    
    // Clear video
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    // Reset speaking state
    isSpeakingRef.current = false;
    
    // Stop Web Speech Recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
      console.log('Stopped Web Speech Recognition');
    }
    
    // Stop any playing audio
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
    
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    // Longer delay to ensure backend has saved the results
    console.log('⏳ Waiting for backend to save results...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Fetch interview result
    if (selectedInterview) {
      try {
        console.log('📊 Fetching interview results...');
        const resultResponse = await interviewAPI.getResult(selectedInterview.id);
        setInterviewResult(resultResponse.data);
        await loadInterviews();
        setLoading(false);
        setView('result');
        console.log('✅ Results loaded successfully!');
      } catch (err: any) {
        console.error('❌ Error fetching result:', err);
        console.error('Error details:', err.response?.data);
        
        // Retry once after another delay
        console.log('🔄 Retrying after 2 seconds...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        try {
          const retryResponse = await interviewAPI.getResult(selectedInterview.id);
          setInterviewResult(retryResponse.data);
          await loadInterviews();
          setLoading(false);
          setView('result');
          console.log('✅ Results loaded on retry!');
        } catch (retryErr) {
          console.error('❌ Retry failed:', retryErr);
          setLoading(false);
          setError('Failed to load interview results. The interview was completed but results are still processing. Please check the dashboard in a moment.');
          setView('dashboard');
        }
      }
    }
  };

  const handleEndInterview = async () => {
    console.log('🛑 User manually ending interview...');
    setLoading(true);
    setError('');
    
    // Signal audio complete
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'audio_complete' }));
    }
    
    // Stop recording
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
    
    // Stop all media tracks (audio and video)
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log('Stopped track:', track.kind);
      });
      streamRef.current = null;
    }
    
    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    // Clear analyser
    analyserRef.current = null;
    
    // Clear silence timeout
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }
    
    // Clear video
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    // Reset speaking state
    isSpeakingRef.current = false;
    
    // Stop Web Speech Recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
      console.log('Stopped Web Speech Recognition');
    }
    
    // Stop any playing audio
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
    
    // Close WebSocket and send end signal
    if (wsRef.current) {
      // Send end signal to trigger backend report generation
      if (wsRef.current.readyState === WebSocket.OPEN) {
        console.log('📤 Sending end_interview signal to backend...');
        wsRef.current.send(JSON.stringify({ type: 'end_interview' }));
      }
      wsRef.current.close();
      wsRef.current = null;
    }
    
    // Longer delay for backend to generate and save report
    console.log('⏳ Waiting for backend to generate report...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Fetch interview result
    if (selectedInterview) {
      try {
        console.log('📊 Fetching interview results...');
        const resultResponse = await interviewAPI.getResult(selectedInterview.id);
        setInterviewResult(resultResponse.data);
        await loadInterviews();
        setLoading(false);
        setView('result');
        console.log('✅ Results loaded successfully!');
      } catch (err: any) {
        console.error('❌ Error fetching result:', err);
        console.error('Error details:', err.response?.data);
        
        // Retry once after another delay
        console.log('🔄 Retrying after 3 seconds...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        try {
          const retryResponse = await interviewAPI.getResult(selectedInterview.id);
          setInterviewResult(retryResponse.data);
          await loadInterviews();
          setLoading(false);
          setView('result');
          console.log('✅ Results loaded on retry!');
        } catch (retryErr) {
          console.error('❌ Retry failed:', retryErr);
          setLoading(false);
          setError('Failed to load interview results. The interview was completed but results are still processing. Please check the dashboard in a moment.');
          setView('dashboard');
        }
      }
    }
  };

  const handleViewResult = async (interviewId: string) => {
    try {
      setLoading(true);
      const resultResponse = await interviewAPI.getResult(interviewId);
      const interviewResponse = await interviewAPI.get(interviewId);
      setInterviewResult(resultResponse.data);
      setSelectedInterview(interviewResponse.data);
      setView('result');
    } catch (err) {
      console.error('Error loading result:', err);
      setError('Failed to load interview result');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteInterview = async (interviewId: string) => {
    if (!window.confirm('Are you sure you want to delete this interview?')) return;
    
    try {
      await interviewAPI.delete(interviewId);
      await loadInterviews();
    } catch (err: any) {
      console.error('Error deleting interview:', err);
      setError(err.response?.data?.detail || 'Failed to delete interview');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'in_progress':
        return '#f59e0b';
      case 'draft':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return '#10b981';
      case 'medium':
        return '#f59e0b';
      case 'hard':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  // Render Dashboard View
  const renderDashboard = () => (
    <div className="interview-dashboard">
      <div className="page-header">
        <div className="page-title">
          <h1>Mock Interviews</h1>
          <p>Practice with AI-powered interview simulations</p>
          </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={loadInterviews} disabled={loading}>
            <RefreshCw size={18} />
            Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setView('create')}>
            <Plus size={20} />
            Create Interview
          </button>
        </div>
      </div>

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
          <p>Loading interviews...</p>
        </div>
      ) : interviews.length === 0 ? (
        <div className="empty-state">
          <Brain size={64} color="#94a3b8" />
          <h3>No Interviews Yet</h3>
          <p>Create your first mock interview to start practicing</p>
          <button className="btn btn-primary btn-large" onClick={() => setView('create')}>
            <Plus size={20} />
            Create Interview
          </button>
        </div>
      ) : (
        <div className="interviews-grid">
          {interviews.map((interview) => (
            <div key={interview.id} className={`interview-card ${interview.status}`}>
              <div className="interview-card-header">
                <div className="interview-type-badge" style={{ background: getStatusColor(interview.status) }}>
                  {interview.interview_type}
                </div>
                <div className="interview-card-actions">
                  {interview.status === 'completed' && (
                    <button 
                      className="icon-btn"
                      onClick={() => handleViewResult(interview.id)}
                      title="View Result"
                    >
                      <Eye size={18} />
                    </button>
                  )}
                  {interview.status === 'draft' && (
                    <button 
                      className="icon-btn danger"
                      onClick={() => handleDeleteInterview(interview.id)}
                      title="Delete"
                    >
                      <Trash2 size={18} />
                    </button>
                  )}
                </div>
              </div>

              <div className="interview-card-body">
                <h3>{interview.target_role}</h3>
                <div className="interview-meta">
                  <span className="meta-item">
                    <Target size={14} />
                    {interview.num_questions} Questions
                  </span>
                  <span className="meta-item difficulty" style={{ color: getDifficultyColor(interview.difficulty) }}>
                    {interview.difficulty}
                  </span>
                </div>

                <div className="interview-technologies">
                  {interview.technologies.slice(0, 3).map((tech, idx) => (
                    <span key={idx} className="tech-badge">{tech}</span>
                  ))}
                  {interview.technologies.length > 3 && (
                    <span className="tech-badge">+{interview.technologies.length - 3}</span>
                  )}
                </div>

                <div className="interview-date">
                  <Calendar size={14} />
                  <span>{formatDate(interview.created_at)}</span>
                </div>
              </div>

              <div className="interview-card-footer">
                {interview.status === 'draft' && (
                  <button 
                    className="btn btn-primary btn-block"
                    onClick={() => handleStartInterview(interview)}
                  >
                    <Play size={18} />
                    Start Interview
                  </button>
                )}
                {interview.status === 'completed' && (
                  <button 
                    className="btn btn-secondary btn-block"
                    onClick={() => handleViewResult(interview.id)}
                  >
                    <Eye size={18} />
                    View Report
                  </button>
                )}
                {interview.status === 'in_progress' && (
                  <button 
                    className="btn btn-success btn-block"
                    onClick={() => handleStartInterview(interview)}
                  >
                    <Play size={18} />
                    Resume Interview
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Render Create Interview Form
  const renderCreateForm = () => (
    <div className="interview-create">
      <div className="create-header">
        <button className="back-btn" onClick={() => setView('dashboard')}>
          <X size={20} />
        </button>
        <div>
          <h1>Create Mock Interview</h1>
          <p>Customize your interview session</p>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      <div className="create-form">
              <div className="form-group">
                <label htmlFor="interview_type">Interview Type</label>
                <select
                  id="interview_type"
            value={createForm.interview_type}
            onChange={(e) => setCreateForm({ ...createForm, interview_type: e.target.value })}
            className="form-select"
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
                  id="target_role"
            type="text"
            value={createForm.target_role}
            onChange={(e) => setCreateForm({ ...createForm, target_role: e.target.value })}
            placeholder="e.g., Software Engineer, Data Scientist"
            className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="technologies">Technologies (comma separated)</label>
                <input
                  id="technologies"
            type="text"
            value={createForm.technologies.join(', ')}
            onChange={(e) => setCreateForm({ 
              ...createForm, 
              technologies: e.target.value.split(',').map(t => t.trim())
            })}
            placeholder="e.g., JavaScript, React, Node.js, Python"
            className="form-input"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
            <label htmlFor="difficulty">Difficulty Level</label>
                  <select
                    id="difficulty"
              value={createForm.difficulty}
              onChange={(e) => setCreateForm({ ...createForm, difficulty: e.target.value })}
              className="form-select"
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
              value={createForm.num_questions}
              onChange={(e) => setCreateForm({ ...createForm, num_questions: parseInt(e.target.value) })}
              className="form-select"
            >
              <option value={3}>3 Questions (~10 min)</option>
              <option value={5}>5 Questions (~15 min)</option>
              <option value={10}>10 Questions (~30 min)</option>
              <option value={15}>15 Questions (~45 min)</option>
                  </select>
                </div>
              </div>

        <div className="form-actions">
          <button className="btn btn-secondary btn-large" onClick={() => setView('dashboard')}>
            Cancel
          </button>
              <button
                className="btn btn-primary btn-large"
            onClick={handleCreateInterview}
            disabled={loading || !createForm.target_role.trim()}
              >
            {loading ? 'Creating...' : 'Create Interview'}
              </button>
            </div>
          </div>
        </div>
  );

  // Render Conversational Interview Session (Video Call Style)
  const renderConversationalSession = () => {
    if (!selectedInterview) {
      return (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading interview...</p>
        </div>
      );
    }

    // Get the last AI message for caption
    const lastAiMessage = chatMessages.length > 0 && chatMessages[chatMessages.length - 1].role === 'ai' 
      ? chatMessages[chatMessages.length - 1].message 
      : null;

    return (
      <div className="interview-video-call-split">
        {/* Header */}
        <div className="video-call-header">
          <div className="interview-info">
            <Brain size={20} />
            <span>{selectedInterview.target_role} Interview</span>
          </div>
          <button 
            className="btn-end-call"
            onClick={handleEndInterview}
            title="End Interview"
          >
            <X size={20} />
            End Interview
          </button>
        </div>

        {/* Split Screen Container */}
        <div className="split-screen-container">
          {/* Left Side - User Video */}
          <div className="user-video-panel">
            <video 
              ref={videoRef}
              autoPlay 
              playsInline 
              muted
              className="user-video-feed"
            />
            <div className="user-label">
              <User size={16} />
              <span>You</span>
            </div>
          </div>

          {/* Right Side - AI Interviewer */}
          <div className="ai-panel">
            {/* AI Avatar (Top) */}
            <div className="ai-interviewer-section">
              <div className={`ai-avatar-large ${isAiSpeaking ? 'speaking' : ''}`}>
                <Brain size={64} />
              </div>
              <h3>AI Interviewer</h3>
              <div className="ai-status">
                {isAiSpeaking ? (
                  <>
                    <div className="status-dot pulse ai"></div>
                    <span>Speaking</span>
                  </>
                ) : isThinking ? (
                  <>
                    <div className="status-dot thinking"></div>
                    <span>Thinking...</span>
                  </>
                ) : (
                  <>
                    <div className="status-dot listening"></div>
                    <span>Listening</span>
                  </>
                )}
              </div>
            </div>

            {/* Captions Section (Bottom) */}
            <div className="captions-section">
              <div className="captions-box">
                {/* AI Speaking Caption */}
                {isAiSpeaking && lastAiMessage && (
                  <div className="caption-bubble ai-bubble">
                    <div className="caption-header">
                      <Brain size={14} />
                      <span>AI Interviewer</span>
                    </div>
                    <div className="caption-text">{lastAiMessage}</div>
                  </div>
                )}

                {/* Thinking Indicator */}
                {isThinking && !isAiSpeaking && (
                  <div className="caption-bubble ai-bubble thinking">
                    <div className="caption-header">
                      <Brain size={14} />
                      <span>AI Interviewer</span>
                    </div>
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}

                {/* User Speaking Caption (Real-time - only current speech) */}
                {!isAiSpeaking && currentTranscript && (
                  <div className="caption-bubble user-bubble">
                    <div className="caption-header">
                      <User size={14} />
                      <span>You</span>
                      <span className="live-badge">● LIVE</span>
                    </div>
                    <div className="caption-text">{currentTranscript}</div>
                  </div>
                )}

                {/* Idle State */}
                {!isAiSpeaking && !isThinking && !currentTranscript && (
                  <div className="caption-bubble idle-bubble">
                    <Mic size={20} />
                    <p>Speak to continue the conversation...</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Loading Overlay for Result Generation */}
        {loading && (
          <div className="interview-loading-overlay">
            <div className="loading-content">
              <div className="spinner"></div>
              <h3>Generating Your Interview Report...</h3>
              <p>Please wait while we analyze your performance</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render Interview Session (Structured Mode)
  const renderSession = () => {
    console.log('Rendering session, view:', view, 'selectedInterview:', selectedInterview);
    
    // Check if conversational mode
    if (interviewStyle === 'conversational') {
      return renderConversationalSession();
    }
    
    if (!selectedInterview) {
      console.log('No selected interview, showing loading...');
      return (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading interview...</p>
        </div>
      );
    }
    
    // Safely get current question
    const currentQuestion = selectedInterview.questions && selectedInterview.questions.length > 0 
      ? selectedInterview.questions[currentQuestionIndex] 
      : null;
    
    console.log('Current question:', currentQuestion, 'Index:', currentQuestionIndex);
    
    const totalQuestions = selectedInterview.questions?.length || selectedInterview.num_questions || 10;
    const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;

    return (
      <div className="interview-session">
        <div className="session-header">
          <div className="progress-info">
            <span>Question {currentQuestionIndex + 1} of {totalQuestions}</span>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>
              </div>
          <div className="session-timer">
                <Clock size={20} />
                <span className={timeLeft < 30 ? 'time-warning' : ''}>{formatTime(timeLeft)}</span>
              </div>
            </div>

        <div className="session-content">
          <div className="ai-interviewer">
            <div className="ai-avatar-large">
              <Brain size={48} color="#fff" />
              {isRecording && (
                <div className="pulse-ring"></div>
              )}
              </div>
            <h3>AI Interviewer</h3>
            <p className="ai-status">{isRecording ? 'Listening...' : 'Waiting'}</p>
          </div>

          <div className="question-display">
            <div className="question-badge">{currentQuestion?.category || selectedInterview.interview_type}</div>
            <h2 className="question-text">
              {currentQuestion?.question_text || currentQuestion?.text || 'Loading question...'}
            </h2>
            {!currentQuestion && (
              <p style={{ textAlign: 'center', color: '#6b7280', marginTop: '1rem' }}>
                Please wait while we prepare your interview questions...
              </p>
            )}
            
            {currentQuestion?.hints && currentQuestion.hints.length > 0 && (
                <div className="question-hints">
                <h4>💡 Hints:</h4>
                  <ul>
                  {currentQuestion.hints.map((hint: string, idx: number) => (
                      <li key={idx}>{hint}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

          <div className="transcript-panel">
            <h4>
              <MessageSquare size={18} />
              Your Response (Real-time Transcript)
            </h4>
            <div className="transcript-box">
              {transcript || 'Start speaking... Your voice is being transcribed in real-time.'}
            </div>
                {isRecording && (
              <div className="recording-indicator">
                    <div className="recording-dot"></div>
                <span>Recording</span>
              </div>
                )}
              </div>

          <div className="session-controls">
            <button 
              className={`control-btn ${!audioEnabled ? 'disabled' : ''}`}
              onClick={() => setAudioEnabled(!audioEnabled)}
            >
              {audioEnabled ? <Mic size={24} /> : <MicOff size={24} />}
              <span>{audioEnabled ? 'Mute' : 'Unmute'}</span>
                </button>
            
            <button className="btn btn-secondary" onClick={handleNextQuestion}>
              Skip
                </button>
            
            <button className="btn btn-primary" onClick={handleNextQuestion}>
              <SkipForward size={20} />
              Next Question
            </button>
            
            <button className="btn btn-danger" onClick={handleEndInterview}>
              End Interview
            </button>
                  </div>
        </div>
      </div>
    );
  };

  // Render Results View
  const renderResult = () => {
    if (!interviewResult || !selectedInterview) return null;

    return (
        <div className="interview-result">
        <div className="result-header">
          <button className="back-btn" onClick={() => {
            setView('dashboard');
            setInterviewResult(null);
            setSelectedInterview(null);
          }}>
            <X size={20} />
          </button>
          <div>
            <h1>Interview Complete!</h1>
            <p>{selectedInterview.target_role} - {selectedInterview.interview_type}</p>
              </div>
            </div>

        <div className="result-content">
          {/* Overall Score */}
          <div className="result-hero">
            <div className="score-circle-xl">
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
                  strokeDashoffset={565.5 - (565.5 * interviewResult.overall_score) / 100}
                      strokeLinecap="round"
                      transform="rotate(-90 100 100)"
                    />
                  </svg>
                  <div className="score-text">
                <span className="score-number">{interviewResult.overall_score}</span>
                    <span className="score-label">/ 100</span>
                  </div>
                </div>
            <div className="score-summary">
              <h2>Overall Score</h2>
              <p>{interviewResult.summary}</p>
            </div>
              </div>

          {/* Detailed Feedback */}
          {interviewResult.detailed_feedback && (
            <div className="feedback-grid">
              {Object.entries(interviewResult.detailed_feedback).map(([key, value]: [string, any]) => (
                <div key={key} className="feedback-metric">
                  <span className="metric-label">{key.replace(/_/g, ' ')}</span>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill" 
                      style={{ width: `${typeof value === 'number' ? value : 75}%` }}
                    ></div>
                    </div>
                  <span className="metric-value">{typeof value === 'number' ? value : 75}%</span>
                  </div>
              ))}
                    </div>
          )}

          {/* Strengths and Improvements */}
          <div className="feedback-sections">
              <div className="feedback-box strengths">
                <h3>
                  <CheckCircle size={24} color="#10b981" />
                  Strengths
                </h3>
                <ul>
                {interviewResult.strengths.map((strength, idx) => (
                  <li key={idx}>{strength}</li>
                ))}
                </ul>
              </div>

              <div className="feedback-box improvements">
                <h3>
                <TrendingUp size={24} color="#f59e0b" />
                  Areas for Improvement
                </h3>
                <ul>
                {interviewResult.improvement_areas.map((area, idx) => (
                  <li key={idx}>{area}</li>
                ))}
                </ul>
              </div>
            </div>

          {/* Transcript - Chat Style */}
          {interviewResult.transcript && interviewResult.transcript.length > 0 && (
            <div className="transcript-section">
              <h3>
                <FileText size={24} />
                Full Conversation Transcript
              </h3>
              <div className="chat-transcript">
                {interviewResult.transcript.map((item: any, idx: number) => {
                  const isInterviewer = item.role === 'interviewer';
                  const isCandidate = item.role === 'candidate';
                  
                  return (
                    <div 
                      key={idx} 
                      className={`chat-message ${isInterviewer ? 'interviewer-msg' : 'candidate-msg'}`}
                    >
                      <div className="message-header">
                        <div className="message-avatar">
                          {isInterviewer ? (
                            <Brain size={18} />
                          ) : (
                            <User size={18} />
                          )}
                        </div>
                        <div className="message-info">
                          <span className="message-sender">
                            {isInterviewer ? 'AI Interviewer' : 'You'}
                          </span>
                          {item.topic && (
                            <span className="message-topic">{item.topic}</span>
                          )}
                        </div>
                        {item.timestamp && item.timestamp !== 'start' && (
                          <span className="message-time">{item.timestamp}</span>
                        )}
                      </div>
                      <div className="message-content">
                        {item.message || item.question_text || item.answer_text || 'No message'}
                      </div>
                      {item.is_complete && (
                        <div className="interview-complete-badge">
                          <CheckCircle size={14} />
                          <span>Interview Completed</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Actions */}
            <div className="result-actions">
            <button 
              className="btn btn-secondary btn-large"
              onClick={() => {
                setView('create');
                setInterviewResult(null);
                setSelectedInterview(null);
              }}
            >
              <RefreshCw size={20} />
                Practice Again
              </button>
            <button 
              className="btn btn-primary btn-large"
              onClick={() => {
                setView('dashboard');
                setInterviewResult(null);
                setSelectedInterview(null);
              }}
            >
              Back to Dashboard
              </button>
          </div>
        </div>
      </div>
    );
  };

  // Main render
  console.log('InterviewPage render, current view:', view);
  
  return (
    <div className="interview-page">
      {view === 'dashboard' && renderDashboard()}
      {view === 'create' && renderCreateForm()}
      {view === 'session' && renderSession()}
      {view === 'result' && renderResult()}
    </div>
  );
};

export default InterviewPage;
