from typing import List, Dict, Any, Optional
import json
import google.generativeai as genai
from app.config import settings
from app.services.voice_service import voice_service

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class VoiceInterviewAgent:
    """
    Enhanced interview agent with voice support
    """
    
    def __init__(
        self,
        interview_type: str,
        target_role: str,
        questions: List[Dict[str, Any]],
        resume_data: Dict[str, Any]
    ):
        self.interview_type = interview_type
        self.target_role = target_role
        self.questions = questions
        self.resume_data = resume_data
        self.current_question_index = 0
        self.total_questions = len(questions)
        self.scores = []
        self.feedback_history = []
        self.voice_analytics = []
        self.is_complete = False
        
        # Initialize Gemini
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.system_context = self._create_system_context()
    
    
    def _create_system_context(self) -> str:
        """Create system context"""
        resume_summary = ""
        if self.resume_data:
            skills = self.resume_data.get("skills", [])
            experience = self.resume_data.get("experience", [])
            resume_summary = f"""
Candidate's Background:
- Skills: {', '.join(skills[:10]) if skills else 'Not provided'}
- Experience: {len(experience)} position(s)
"""
        
        return f"""You are an expert interviewer conducting a {self.interview_type} interview for a {self.target_role} position.

{resume_summary}

Evaluate answers based on:
1. Technical accuracy and depth
2. Communication clarity (now including voice analysis)
3. Practical understanding
4. Confidence in delivery

Score 1-10 with honest, constructive feedback."""
    
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get current question"""
        if self.current_question_index < self.total_questions:
            return self.questions[self.current_question_index]
        return None
    
    
    def get_question_audio(self, question_text: str) -> bytes:
        """
        Generate audio for the question using TTS
        
        Args:
            question_text: Question to convert to speech
            
        Returns:
            Audio data as bytes (MP3)
        """
        return voice_service.synthesize_speech(question_text)
    
    
    async def transcribe_answer(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Transcribe user's audio answer to text
        
        Args:
            audio_data: Raw audio bytes from user
            
        Returns:
            Dict with transcript and voice analysis
        """
        # Transcribe audio to text
        transcription = voice_service.transcribe_audio(audio_data)
        
        if transcription.get("error"):
            return {
                "transcript": "",
                "confidence": 0.0,
                "voice_analysis": None,
                "error": transcription["error"]
            }
        
        # Analyze voice characteristics
        word_timings = transcription.get("word_timings", [])
        transcript = transcription.get("transcript", "")
        
        voice_analysis = voice_service.analyze_voice_characteristics(
            word_timings, transcript
        )
        
        return {
            "transcript": transcript,
            "confidence": transcription.get("confidence", 0.0),
            "voice_analysis": voice_analysis,
            "error": None
        }
    
    
    async def evaluate_answer(
        self, 
        answer: str, 
        voice_analysis: Optional[Dict[str, Any]] = None,
        time_taken: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluate answer with voice analysis integration
        """
        current_question = self.questions[self.current_question_index]
        
        # Include voice analysis in prompt
        voice_context = ""
        if voice_analysis:
            voice_context = f"""

Voice Analysis:
- Words per minute: {voice_analysis['words_per_minute']} ({voice_analysis['pace']} pace)
- Filler words: {voice_analysis['filler_words_count']} ({voice_analysis['filler_words_percentage']}%)
- Confidence score: {voice_analysis['confidence_score']}/100
- Long pauses: {voice_analysis.get('long_pauses', 0)}
"""
        
        prompt = f"""{self.system_context}

Question #{self.current_question_index + 1}: {current_question['text']}

Expected Points: {', '.join(current_question['expected_points'])}

Candidate's Answer:
"{answer}"

{voice_context}

Time taken: {time_taken} seconds

Evaluate considering both content quality AND voice delivery. Provide JSON:
{{
    "score": <1-10>,
    "feedback": "<constructive feedback including voice delivery>",
    "strengths": ["strength 1", "strength 2"],
    "improvements": ["area 1", "area 2"],
    "follow_up": null
}}

Return ONLY valid JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean markdown fences (handle ```json, ``` and trailing ```)
            if content.startswith("```json"):
                content = content[len("```json"):].lstrip()
            if content.startswith("```"):
                content = content[len("```"):].lstrip()
            if content.endswith("```"):
                content = content[:-3].rstrip()
            content = content.strip()
            
            evaluation = json.loads(content)
            evaluation["score"] = max(1, min(10, int(evaluation.get("score", 5))))
            
        except Exception as e:
            print(f"Evaluation error: {e}")
            evaluation = {
                "score": 6,
                "feedback": "Good answer. Consider providing more specific examples.",
                "strengths": ["Clear communication"],
                "improvements": ["Add more technical depth"],
                "follow_up": None
            }
        
        # Store results
        self.scores.append(evaluation["score"])
        self.feedback_history.append({
            "question_number": self.current_question_index + 1,
            "question_text": current_question["text"],
            "answer": answer,
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
            "voice_analysis": voice_analysis,
            "time_taken": time_taken
        })
        
        if voice_analysis:
            self.voice_analytics.append(voice_analysis)
        
        self.current_question_index += 1
        
        if self.current_question_index >= self.total_questions:
            self.is_complete = True
        
        return evaluation
    
    
    async def generate_final_report(self) -> Dict[str, Any]:
        """Generate final report with voice analysis"""
        
        if not self.scores:
            return {
                "overall_score": 0,
                "summary": "No answers evaluated.",
                "detailed_feedback": {},
                "strengths": [],
                "improvement_areas": [],
                "voice_summary": {},
                "transcript": []
            }
        
        overall_score = int(sum(self.scores) / len(self.scores))
        
        # Calculate average voice metrics
        if self.voice_analytics:
            avg_wpm = sum(v['words_per_minute'] for v in self.voice_analytics) / len(self.voice_analytics)
            avg_confidence = sum(v['confidence_score'] for v in self.voice_analytics) / len(self.voice_analytics)
            total_fillers = sum(v['filler_words_count'] for v in self.voice_analytics)
            
            voice_summary = {
                "average_words_per_minute": round(avg_wpm, 1),
                "average_confidence_score": round(avg_confidence, 1),
                "total_filler_words": total_fillers,
                "speaking_pace": "normal" if 100 <= avg_wpm <= 160 else ("slow" if avg_wpm < 100 else "fast")
            }
        else:
            voice_summary = {}
        
        # Generate AI summary
        prompt = f"""{self.system_context}

Interview Complete
Overall Score: {overall_score}/10

Performance:
{json.dumps(self.feedback_history, indent=2)}

Voice Metrics:
{json.dumps(voice_summary, indent=2)}

Generate comprehensive JSON summary:
{{
    "summary": "<2-3 sentence assessment including voice delivery>",
    "detailed_feedback": {{
        "technical_depth": <1-10>,
        "communication": <1-10>,
        "problem_solving": <1-10>,
        "confidence": <1-10>,
        "voice_delivery": <1-10>
    }},
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "improvement_areas": ["area 1", "area 2", "area 3"],
    "recommendation": "<hire|consider|not recommended>",
    "next_steps": "<advice>"
}}

Return ONLY valid JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean markdown fences (handle ```json, ``` and trailing ```)
            if content.startswith("```json"):
                content = content[len("```json"):].lstrip()
            if content.startswith("```"):
                content = content[len("```"):].lstrip()
            if content.endswith("```"):
                content = content[:-3].rstrip()
            content = content.strip()
            
            report = json.loads(content)
            
        except Exception as e:
            print(f"Report error: {e}")
            report = {
                "summary": f"Completed with score {overall_score}/10.",
                "detailed_feedback": {
                    "technical_depth": overall_score,
                    "communication": overall_score,
                    "problem_solving": overall_score,
                    "confidence": overall_score,
                    "voice_delivery": overall_score
                },
                "strengths": ["Completed all questions"],
                "improvement_areas": ["Continue practicing"],
                "recommendation": "consider",
                "next_steps": "Keep improving"
            }
        
        return {
            "overall_score": overall_score,
            "summary": report.get("summary", ""),
            "detailed_feedback": report.get("detailed_feedback", {}),
            "strengths": report.get("strengths", []),
            "improvement_areas": report.get("improvement_areas", []),
            "recommendation": report.get("recommendation", ""),
            "next_steps": report.get("next_steps", ""),
            "voice_summary": voice_summary,
            "transcript": self.feedback_history
        }
    
    
    def get_progress(self) -> Dict[str, Any]:
        """Get progress"""
        return {
            "current_question": self.current_question_index + 1,
            "total_questions": self.total_questions,
            "completed": self.current_question_index,
            "remaining": self.total_questions - self.current_question_index,
            "is_complete": self.is_complete
        }
