from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import uuid
import base64
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.interview import Interview, InterviewResult
from app.core.security import decode_token
from app.core.exceptions import AuthenticationException
from app.agents.voice_interview_agent import VoiceInterviewAgent
from app.agents.conversational_interview_agent import ConversationalInterviewAgent
from app.services.interview_service import InterviewService

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
    
    async def send_json(self, connection_id: str, data: dict):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(data)
    
    async def send_bytes(self, connection_id: str, data: bytes):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_bytes(data)


manager = ConnectionManager()


async def get_current_user_ws(token: str, db: Session) -> User:
    """Authenticate WebSocket connection"""
    payload = decode_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise AuthenticationException("Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid token payload")
    
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    if not user or not user.is_active:
        raise AuthenticationException("User not found or inactive")
    
    return user


@router.websocket("/interview/{interview_id}")
async def voice_interview_websocket(
    websocket: WebSocket,
    interview_id: str,
    token: str = Query(...),
    mode: str = Query("voice"),  # "voice" or "text"
    style: str = Query("conversational"),  # "conversational" or "structured"
    db: Session = Depends(get_db)
):
    """
    Real-time Voice Interview WebSocket
    
    Modes:
    - voice: Full voice mode (audio in/out)
    - text: Text mode (text in/out)
    
    Message Types:
    
    Client → Server:
    1. {"type": "audio_chunk", "data": "<base64_audio>"}  # Voice mode
    2. {"type": "answer", "answer_text": "..."}            # Text mode
    3. {"type": "audio_complete"}                          # Signal end of audio
    4. {"type": "ping"}                                    # Keep-alive
    
    Server → Client:
    1. {"type": "welcome", "message": "...", "mode": "voice"}
    2. {"type": "question_audio", "data": "<base64_audio>", "question": {...}}
    3. {"type": "question_text", "question": {...}}
    4. {"type": "transcription", "text": "...", "confidence": 0.95}
    5. {"type": "feedback", "score": 8, "feedback": "...", ...}
    6. {"type": "interview_complete", "report": {...}}
    """
    
    connection_id = f"{interview_id}_{uuid.uuid4()}"
    
    # Accept connection first (required for proper error handling)
    await websocket.accept()
    
    try:
        # Authenticate after accepting connection
        try:
            user = await get_current_user_ws(token, db)
        except Exception as e:
            await websocket.close(code=4001, reason=f"Authentication failed: {str(e)}")
            return
        
        # Get interview
        interview = db.query(Interview).filter(
            Interview.id == uuid.UUID(interview_id),
            Interview.user_id == user.id
        ).first()
        
        if not interview:
            await websocket.close(code=4004, reason="Interview not found")
            return
        
        if interview.status == "completed":
            await websocket.close(code=4000, reason="Interview already completed")
            return
        
        # Add to connection manager
        manager.active_connections[connection_id] = websocket
        
        # Update interview status
        if interview.status == "draft":
            interview.status = "in_progress"
            interview.started_at = datetime.utcnow()
            db.commit()
        
        # Get resume
        resume_data = InterviewService.get_user_resume(db, user.id)
        
        # Initialize appropriate agent based on style
        if style == "conversational":
            agent = ConversationalInterviewAgent(
                interview_type=interview.interview_type,
                target_role=interview.target_role,
                technologies=interview.technologies,
                difficulty=interview.difficulty,
                resume_data=resume_data
            )
            
            # Get initial greeting
            initial_message = await agent.get_initial_message()
            
            # Send welcome with initial greeting
            await manager.send_json(connection_id, {
                "type": "welcome",
                "style": "conversational",
                "mode": mode
            })
            
            # Send AI's initial message
            await manager.send_json(connection_id, {
                "type": "ai_message",
                "message": initial_message["message"],
                "topic": initial_message.get("topic")
            })
            
            # Generate and send audio if voice mode
            if mode == "voice":
                audio_data = agent.get_question_audio(initial_message["message"])
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    await manager.send_json(connection_id, {
                        "type": "ai_audio",
                        "data": audio_base64,
                        "format": "mp3"
                    })
        else:
            # Original structured mode
            agent = VoiceInterviewAgent(
                interview_type=interview.interview_type,
                target_role=interview.target_role,
                questions=interview.questions,
                resume_data=resume_data
            )
            
            # Send welcome message
            await manager.send_json(connection_id, {
                "type": "welcome",
                "message": f"Welcome to your {interview.interview_type} interview for {interview.target_role}",
                "style": "structured",
                "mode": mode,
                "total_questions": agent.total_questions
            })
            
            # Send first question
            await send_next_question(connection_id, agent, mode)
        
        # Audio buffer for voice mode
        audio_buffer = bytearray()
        
        # Listen for messages
        while True:
            # Receive message
            message = await websocket.receive()
            
            # Handle different message types
            if "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")
                
                if msg_type == "audio_chunk":
                    # Voice mode: accumulate audio chunks
                    if mode == "voice":
                        audio_data = base64.b64decode(data.get("data", ""))
                        audio_buffer.extend(audio_data)
                
                elif msg_type == "audio_complete":
                    # Voice mode: process complete audio
                    if mode == "voice" and audio_buffer:
                        if style == "conversational":
                            await process_conversational_voice(
                                connection_id, agent, bytes(audio_buffer), mode, db, interview, user
                            )
                        else:
                            await process_voice_answer(
                                connection_id, agent, bytes(audio_buffer), db, interview, user
                            )
                        audio_buffer.clear()
                
                elif msg_type == "user_message":
                    # Conversational mode: process user's message
                    if style == "conversational":
                        message_text = data.get("message", "")
                        if not message_text:
                            await manager.send_json(connection_id, {
                                "type": "error",
                                "message": "Message cannot be empty"
                            })
                            continue
                        
                        await process_conversational_message(
                            connection_id, agent, message_text, mode, db, interview, user
                        )
                
                elif msg_type == "answer":
                    # Text mode: process text answer
                    if mode == "text":
                        answer_text = data.get("answer_text", "")
                        time_taken = data.get("time_taken", 0)
                        
                        if not answer_text:
                            await manager.send_json(connection_id, {
                                "type": "error",
                                "message": "Answer cannot be empty"
                            })
                            continue
                        
                        await process_text_answer(
                            connection_id, agent, answer_text, time_taken, db, interview, user
                        )
                
                elif msg_type == "ping":
                    await manager.send_json(connection_id, {"type": "pong"})
                
                elif msg_type == "end_interview":
                    # User or system wants to end the interview
                    # Generate report and complete properly (not abandon)
                    if style == "conversational":
                        await complete_conversational_interview(
                            connection_id, agent, db, interview, user
                        )
                    else:
                        # For structured mode
                        interview.status = "completed"
                        interview.completed_at = datetime.utcnow()
                        db.commit()
                    break
            
            elif "bytes" in message:
                # Direct binary audio data
                if mode == "voice":
                    audio_buffer.extend(message["bytes"])
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {connection_id}")
        manager.disconnect(connection_id)
        
        if interview.status == "in_progress":
            interview.status = "abandoned"
            db.commit()
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        manager.disconnect(connection_id)
    
    finally:
        manager.disconnect(connection_id)


async def process_conversational_voice(
    connection_id: str,
    agent: ConversationalInterviewAgent,
    audio_data: bytes,
    mode: str,
    db: Session,
    interview: Interview,
    user: User
):
    """Process voice input in conversational mode"""
    
    # Send processing message
    await manager.send_json(connection_id, {
        "type": "processing",
        "message": "Transcribing..."
    })
    
    # Transcribe audio
    transcription_result = await agent.transcribe_answer(audio_data)
    
    if transcription_result.get("error"):
        await manager.send_json(connection_id, {
            "type": "error",
            "message": f"Transcription failed: {transcription_result['error']}"
        })
        return
    
    transcript = transcription_result["transcript"]
    voice_analysis = transcription_result.get("voice_analysis")
    
    # Send transcription to client
    await manager.send_json(connection_id, {
        "type": "transcription",
        "text": transcript
    })
    
    # Process with conversational AI
    await process_conversational_message(
        connection_id, agent, transcript, mode, db, interview, user, voice_analysis
    )


async def process_conversational_message(
    connection_id: str,
    agent: ConversationalInterviewAgent,
    message: str,
    mode: str,
    db: Optional[Session] = None,
    interview: Optional[Interview] = None,
    user: Optional[User] = None,
    voice_analysis: Optional[Dict[str, Any]] = None
):
    """Process user message and generate AI response in conversational mode"""
    
    # Send thinking message
    await manager.send_json(connection_id, {
        "type": "thinking",
        "message": "Thinking..."
    })
    
    # Get AI's response
    ai_response = await agent.process_candidate_response(message, voice_analysis)
    
    # Send AI's message
    await manager.send_json(connection_id, {
        "type": "ai_message",
        "message": ai_response["message"],
        "topic": ai_response.get("topic"),
        "is_complete": ai_response.get("is_complete", False)
    })
    
    # If interview is complete, generate report
    if ai_response.get("is_complete") and db and interview and user:
        await complete_conversational_interview(
            connection_id, agent, db, interview, user
        )
    else:
        # Generate and send audio for AI's message
        if mode == "voice":
            await manager.send_json(connection_id, {
                "type": "generating_audio"
            })
            
            audio_data = agent.get_question_audio(ai_response["message"])
            if audio_data:
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                await manager.send_json(connection_id, {
                    "type": "ai_audio",
                    "data": audio_base64,
                    "format": "mp3"
                })


async def complete_conversational_interview(
    connection_id: str,
    agent: ConversationalInterviewAgent,
    db: Session,
    interview: Interview,
    user: User
):
    """Complete conversational interview and generate report"""
    
    await manager.send_json(connection_id, {
        "type": "generating_report",
        "message": "Generating your interview report..."
    })
    
    # Generate final report
    final_report = await agent.generate_final_report()

    # Coerce fields to match schema expectations (avoid ResponseValidationError)
    overall_score = int(final_report.get("overall_score", 0))
    summary = str(final_report.get("summary", ""))

    detailed_feedback_raw = final_report.get("detailed_feedback")
    # detailed_feedback must be a dict per schema
    if isinstance(detailed_feedback_raw, dict):
        detailed_feedback = detailed_feedback_raw
    elif isinstance(detailed_feedback_raw, str):
        detailed_feedback = {"overall": detailed_feedback_raw}
    else:
        detailed_feedback = {}

    improvement_areas_raw = final_report.get("improvement_areas", [])
    if not isinstance(improvement_areas_raw, list):
        improvement_areas = [str(improvement_areas_raw)] if improvement_areas_raw else []
    else:
        improvement_areas = [str(x) for x in improvement_areas_raw]

    strengths_raw = final_report.get("strengths", [])
    if not isinstance(strengths_raw, list):
        strengths = [str(strengths_raw)] if strengths_raw else []
    else:
        strengths = [str(x) for x in strengths_raw]

    # Ensure transcript is a list of dicts
    transcript_val = final_report.get("transcript")
    if isinstance(transcript_val, list):
        transcript_data = transcript_val
    else:
        transcript_data = agent.conversation_history
    
    # Save to database
    interview_result = InterviewResult(
        interview_id=interview.id,
        user_id=user.id,
        overall_score=overall_score,
        summary=summary,
        detailed_feedback=detailed_feedback,
        improvement_areas=improvement_areas,
        strengths=strengths,
        transcript=transcript_data,
        voice_analysis=None,
        ai_remarks=str(final_report.get("next_steps", ""))
    )
    db.add(interview_result)
    
    # Update interview
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    if interview.started_at:
        interview.duration_seconds = int((datetime.utcnow() - interview.started_at).total_seconds())
    
    db.commit()
    
    # Send complete message
    await manager.send_json(connection_id, {
        "type": "interview_complete",
        "overall_score": overall_score,
        "summary": summary,
        "detailed_feedback": detailed_feedback,
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "category_scores": final_report.get("category_scores"),
        "key_highlights": final_report.get("key_highlights"),
        "recommendation": final_report.get("recommendation"),
        "next_steps": final_report.get("next_steps"),
        "message": "Interview completed successfully!"
    })


async def send_next_question(connection_id: str, agent: VoiceInterviewAgent, mode: str):
    """Send next question to client"""
    
    question = agent.get_current_question()
    if not question:
        return
    
    # Send question metadata
    await manager.send_json(connection_id, {
        "type": "question",
        "question_number": question["id"],
        "question_text": question["text"],
        "category": question["category"],
        "difficulty": question["difficulty"],
        "total_questions": agent.total_questions,
        "mode": mode
    })
    
    # If voice mode, generate and send audio
    if mode == "voice":
        await manager.send_json(connection_id, {
            "type": "generating_audio",
            "message": "Generating question audio..."
        })
        
        # Generate TTS audio
        audio_data = agent.get_question_audio(question["text"])
        
        if audio_data:
            # Send audio as base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            await manager.send_json(connection_id, {
                "type": "question_audio",
                "data": audio_base64,
                "format": "mp3"
            })


async def process_voice_answer(
    connection_id: str,
    agent: VoiceInterviewAgent,
    audio_data: bytes,
    db: Session,
    interview: Interview,
    user: User
):
    """Process voice answer"""
    
    # Send processing message
    await manager.send_json(connection_id, {
        "type": "processing",
        "message": "Transcribing your answer..."
    })
    
    # Transcribe audio
    transcription_result = await agent.transcribe_answer(audio_data)
    
    if transcription_result.get("error"):
        await manager.send_json(connection_id, {
            "type": "error",
            "message": f"Transcription failed: {transcription_result['error']}"
        })
        return
    
    transcript = transcription_result["transcript"]
    voice_analysis = transcription_result.get("voice_analysis")
    
    # Send transcription to client
    await manager.send_json(connection_id, {
        "type": "transcription",
        "text": transcript,
        "confidence": transcription_result.get("confidence", 0.0),
        "voice_analysis": voice_analysis
    })
    
    # Evaluate answer
    await manager.send_json(connection_id, {
        "type": "evaluating",
        "message": "Evaluating your answer..."
    })
    
    evaluation = await agent.evaluate_answer(
        transcript,
        voice_analysis=voice_analysis,
        time_taken=voice_analysis.get("duration_seconds", 0) if voice_analysis else 0
    )
    
    # Send feedback
    await manager.send_json(connection_id, {
        "type": "feedback",
        "question_number": agent.current_question_index,
        "score": evaluation["score"],
        "feedback": evaluation["feedback"],
        "strengths": evaluation.get("strengths", []),
        "improvements": evaluation.get("improvements", [])
    })
    
    # Check if complete
    if agent.is_complete:
        await complete_interview(connection_id, agent, db, interview, user)
    else:
        # Send next question
        await send_next_question(connection_id, agent, "voice")


async def process_text_answer(
    connection_id: str,
    agent: VoiceInterviewAgent,
    answer_text: str,
    time_taken: int,
    db: Session,
    interview: Interview,
    user: User
):
    """Process text answer"""
    
    await manager.send_json(connection_id, {
        "type": "processing",
        "message": "Evaluating your answer..."
    })
    
    # Evaluate (no voice analysis for text mode)
    evaluation = await agent.evaluate_answer(answer_text, time_taken=time_taken)
    
    # Send feedback
    await manager.send_json(connection_id, {
        "type": "feedback",
        "question_number": agent.current_question_index,
        "score": evaluation["score"],
        "feedback": evaluation["feedback"],
        "strengths": evaluation.get("strengths", []),
        "improvements": evaluation.get("improvements", [])
    })
    
    # Check if complete
    if agent.is_complete:
        await complete_interview(connection_id, agent, db, interview, user)
    else:
        # Send next question
        await send_next_question(connection_id, agent, "text")


async def complete_interview(
    connection_id: str,
    agent: VoiceInterviewAgent,
    db: Session,
    interview: Interview,
    user: User
):
    """Complete interview and generate report"""
    
    await manager.send_json(connection_id, {
        "type": "generating_report",
        "message": "Generating your interview report..."
    })
    
    # Generate final report
    final_report = await agent.generate_final_report()
    
    # Save to database
    interview_result = InterviewResult(
        interview_id=interview.id,
        user_id=user.id,
        overall_score=final_report["overall_score"],
        summary=final_report["summary"],
        detailed_feedback=final_report["detailed_feedback"],
        improvement_areas=final_report["improvement_areas"],
        strengths=final_report["strengths"],
        transcript=final_report["transcript"],
        voice_analysis=final_report.get("voice_summary"),
        ai_remarks=final_report.get("next_steps", "")
    )
    db.add(interview_result)
    
    # Update interview
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    if interview.started_at:
        interview.duration_seconds = int((datetime.utcnow() - interview.started_at).total_seconds())
    
    db.commit()
    
    # Send complete message
    await manager.send_json(connection_id, {
        "type": "interview_complete",
        "overall_score": final_report["overall_score"],
        "summary": final_report["summary"],
        "detailed_feedback": final_report["detailed_feedback"],
        "strengths": final_report["strengths"],
        "improvement_areas": final_report["improvement_areas"],
        "voice_summary": final_report.get("voice_summary"),
        "recommendation": final_report.get("recommendation"),
        "next_steps": final_report.get("next_steps"),
        "message": "Interview completed successfully!"
    })
