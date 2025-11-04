# PrepMind Interview WebSocket Protocol

## Connection

### Endpoint
```
ws://localhost:8000/api/v1/ws/interview/{interview_id}
```

### Query Parameters
- **token** (required): JWT access token for authentication
- **mode** (optional): `voice` or `text` (default: `voice`)

### Example Connection
```javascript
const token = localStorage.getItem('access_token');
const interviewId = 'uuid-here';
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/interview/${interviewId}?token=${token}&mode=voice`
);
```

## Authentication

The WebSocket requires JWT authentication via the `token` query parameter. If authentication fails, the connection will be rejected with:
- **403 Forbidden**: Invalid or missing token
- **4004**: Interview not found
- **4000**: Interview already completed

## Message Protocol

### Client → Server Messages

#### 1. Audio Chunk (Voice Mode)
Send audio data for real-time transcription:
```json
{
  "type": "audio_chunk",
  "data": "<base64_encoded_audio>"
}
```

#### 2. Answer Submission
Submit the answer to current question:
```json
{
  "type": "answer",
  "question_number": 1,
  "answer_text": "My answer here...",
  "time_taken": 120
}
```

#### 3. Audio Complete Signal
Signal that audio recording is complete:
```json
{
  "type": "audio_complete"
}
```

#### 4. End Interview
Signal interview termination:
```json
{
  "type": "end_interview"
}
```

#### 5. Keep-Alive Ping
Maintain connection (send every 30 seconds):
```json
{
  "type": "ping"
}
```

### Server → Client Messages

#### 1. Welcome Message
Sent immediately after connection:
```json
{
  "type": "welcome",
  "message": "Welcome to your technical interview for Software Engineer",
  "mode": "voice",
  "total_questions": 5
}
```

#### 2. Question (Text Mode)
Question in text format:
```json
{
  "type": "question_text",
  "question": {
    "number": 1,
    "text": "Explain the concept of closures in JavaScript",
    "category": "technical",
    "hints": ["Think about scope", "Consider function returns"]
  }
}
```

#### 3. Question (Voice Mode)
Question with audio:
```json
{
  "type": "question_audio",
  "data": "<base64_encoded_audio>",
  "question": {
    "number": 1,
    "text": "Explain the concept of closures in JavaScript"
  }
}
```

#### 4. Real-time Transcription
Your speech transcribed to text:
```json
{
  "type": "transcription",
  "text": "Closures are functions that have access to...",
  "confidence": 0.95
}
```

#### 5. Feedback
Feedback after answering a question:
```json
{
  "type": "feedback",
  "score": 8,
  "feedback": "Good explanation, but could add more examples",
  "strengths": ["Clear structure", "Good terminology"],
  "improvements": ["Add examples", "Explain use cases"]
}
```

#### 6. Interview Complete
Sent when interview is finished:
```json
{
  "type": "interview_complete",
  "report": {
    "overall_score": 85,
    "summary": "Strong performance overall...",
    "detailed_feedback": {...}
  }
}
```

## Connection Flow

### 1. Initialization
```
Client                          Server
  |                               |
  |--- Connect with token ------->|
  |<----- accept (200) -----------|
  |<----- welcome message --------|
  |<----- first question ---------|
```

### 2. Question-Answer Cycle
```
Client                          Server
  |                               |
  |<----- question audio ---------|
  |                               |
  |--- audio chunks ------------->|
  |<----- transcription ----------|
  |--- audio chunks ------------->|
  |<----- transcription ----------|
  |--- audio_complete ----------->|
  |                               |
  |--- answer ------------------>|
  |<----- feedback --------------|
  |<----- next question ---------|
```

### 3. Termination
```
Client                          Server
  |                               |
  |--- end_interview ------------>|
  |<----- interview_complete -----|
  |--- close connection --------->|
  |<----- close (1000) -----------|
```

## Error Handling

### Connection Errors
- **403**: Authentication failed - token invalid or expired
- **4004**: Interview not found or access denied
- **4000**: Interview already completed
- **1000**: Normal closure
- **1001**: Going away (client/server shutting down)
- **1006**: Abnormal closure (no close frame received)

### Client-Side Error Handling
```javascript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Show user-friendly error message
  // Attempt reconnection if appropriate
};

ws.onclose = (event) => {
  console.log('Connection closed:', event.code, event.reason);
  
  if (event.code === 4000) {
    // Interview already completed - show result
  } else if (event.code === 403 || event.code === 4004) {
    // Authentication or permission issue
    // Redirect to login or dashboard
  } else {
    // Unexpected closure - offer to retry
  }
};
```

## Keep-Alive

Implement periodic ping to keep connection alive:
```javascript
// Send ping every 30 seconds
const pingInterval = setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 30000);

// Clean up on close
ws.onclose = () => {
  clearInterval(pingInterval);
};
```

## Audio Format

### Recording Settings
```javascript
const stream = await navigator.mediaDevices.getUserMedia({ 
  audio: {
    sampleRate: 16000,  // 16kHz recommended
    channelCount: 1,     // Mono
    echoCancellation: true,
    noiseSuppression: true
  }
});

const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm;codecs=opus'
});

// Send chunks every 1 second
mediaRecorder.start(1000);
```

### Base64 Encoding
```javascript
mediaRecorder.ondataavailable = async (event) => {
  const buffer = await event.data.arrayBuffer();
  const base64 = btoa(
    new Uint8Array(buffer).reduce(
      (data, byte) => data + String.fromCharCode(byte), 
      ''
    )
  );
  
  ws.send(JSON.stringify({
    type: 'audio_chunk',
    data: base64
  }));
};
```

## Best Practices

### 1. Connection Management
- Always authenticate before connecting
- Handle connection failures gracefully
- Implement reconnection logic with exponential backoff
- Clean up resources on disconnect

### 2. Audio Streaming
- Send audio chunks of reasonable size (1-2 seconds)
- Buffer audio locally in case of connection issues
- Stop all media tracks on disconnect
- Request microphone permission before connecting

### 3. User Experience
- Show connection status to user
- Display real-time transcript
- Provide feedback on audio quality
- Allow manual override (skip, retry, etc.)

### 4. Error Recovery
```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 3;

function connectWebSocket() {
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    reconnectAttempts = 0; // Reset on successful connection
  };
  
  ws.onclose = (event) => {
    if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
      setTimeout(connectWebSocket, delay);
    }
  };
}
```

## Testing

### Test Connection
```javascript
// Test with minimal setup
const ws = new WebSocket(
  `ws://localhost:8000/ws/interview/${interviewId}?token=${token}&mode=text`
);

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

### Send Test Messages
```javascript
// After connection is open
ws.send(JSON.stringify({ type: 'ping' }));

ws.send(JSON.stringify({
  type: 'answer',
  question_number: 1,
  answer_text: 'Test answer',
  time_taken: 60
}));
```

## Security Considerations

1. **Token Security**: Never expose tokens in logs or error messages
2. **Connection Encryption**: Use WSS (WebSocket Secure) in production
3. **Input Validation**: Validate all incoming messages on both sides
4. **Rate Limiting**: Implement rate limits to prevent abuse
5. **Timeout**: Set reasonable timeouts for inactive connections

## Production Deployment

### Environment Variables
```env
# Frontend
VITE_WS_URL=wss://your-domain.com

# Backend
WEBSOCKET_MAX_SIZE=10485760  # 10MB
WEBSOCKET_PING_INTERVAL=30
WEBSOCKET_PING_TIMEOUT=10
```

### Nginx Configuration (if using reverse proxy)
```nginx
location /ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 86400;
}
```

