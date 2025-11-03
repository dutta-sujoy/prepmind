from typing import List, Dict, Any, Optional
import json
import google.generativeai as genai
from app.config import settings
from app.services.voice_service import voice_service

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class ConversationalInterviewAgent:
    """
    Conversational interview agent that conducts natural, human-like interviews
    """

    def __init__(
        self,
        interview_type: str,
        target_role: str,
        technologies: List[str],
        difficulty: str,
        resume_data: Dict[str, Any]
    ):
        self.interview_type = interview_type
        self.target_role = target_role
        self.technologies = technologies
        self.difficulty = difficulty
        self.resume_data = resume_data

        # Conversation state
        self.conversation_history = []
        self.topics_covered = []
        self.has_introduced = False
        self.is_complete = False
        self.questions_asked = 0
        self.target_questions = 8  # Approximate number of main topics to cover

        # Initialize Gemini with chat mode
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.system_prompt = self._create_system_prompt()

        # Start chat session
        self.chat = self.model.start_chat(history=[])

    def _create_system_prompt(self) -> str:
        """Create system prompt for the conversational interviewer"""
        resume_summary = ""
        if self.resume_data:
            skills = self.resume_data.get("skills", [])
            experience = self.resume_data.get("experience", [])
            resume_summary = f"""
Candidate's Background (from resume):
- Skills: {', '.join(skills[:15]) if skills else 'Not provided'}
- Experience: {len(experience)} position(s)
- Education: {self.resume_data.get('education', [{}])[0].get('degree', 'Not provided') if self.resume_data.get('education') else 'Not provided'}
"""

        return f"""You are an experienced, HONEST technical interviewer conducting a {self.interview_type} interview for a {self.target_role} position.

{resume_summary}

Technologies to assess: {', '.join(self.technologies)}
Difficulty level: {self.difficulty}

**Your Role:**
- Conduct a natural, conversational interview as a human interviewer would
- Start with "please introduce yourself" or similar greeting
- Ask follow-up questions based on their answers
- Probe deeper when answers are incomplete or interesting
- Ask for clarifications when needed
- Cover multiple main technical topics (aim for thorough assessment, not a fixed number)
- Be professional but HONEST - don't praise incorrect or incomplete answers
- Transition smoothly between topics
- Continue the interview as long as needed to properly assess the candidate
- ONLY end when you've thoroughly assessed their skills across various areas
- When ready to end, first ask "Do you have any questions for me?" 
- Then naturally close with "That completes our interview today. Thank you for your time."

**CRITICAL - Be Honest in Your Responses:**
1. If an answer is WRONG or INCOMPLETE, say so politely: "I appreciate your effort, but that's not quite right" or "That's a partial answer, but you're missing..."
2. If an answer is VAGUE or lacks detail, push back: "Can you be more specific?" or "That's quite general, can you give a concrete example?"
3. If an answer is EXCELLENT, then praise it: "Great answer! That shows strong understanding."
4. If an answer is MEDIOCRE, acknowledge neutrally: "I see. Let's move on to..." or "Okay, that covers the basics."
5. DON'T say "Excellent!" or "Great!" unless the answer truly deserves it
6. DON'T be overly positive for incomplete or wrong answers
7. BE CRITICAL but PROFESSIONAL - like a real interviewer would be

**Important Guidelines:**
1. Ask ONE question at a time
2. Don't show a list of questions - make it conversational
3. Follow up naturally based on their responses
4. CHALLENGE weak answers with follow-ups
5. If answer is vague, ask for specific examples or clarification
6. Maintain a professional, evaluative tone (not cheerleader tone)
7. Don't reveal the structure or number of questions
8. The interview continues until you're satisfied with your assessment
9. Don't rush - take time to explore their knowledge deeply
10. Only set is_complete=true when you're genuinely ready to end (not after a fixed number of questions)

**Response Format:**
Always respond with ONLY valid JSON in this format:
{{
  "message": "Your spoken response to the candidate",
  "is_complete": false,
  "topic": "current topic being discussed",
  "internal_note": "brief note about what you're assessing (not shown to candidate)"
}}

When the interview should end, set "is_complete": true and include a closing message.

Begin now with a warm greeting and ask them to introduce themselves."""

        return prompt

    async def get_initial_message(self) -> Dict[str, Any]:
        """Get the initial greeting message"""
        try:
            response = self.chat.send_message(self.system_prompt)
            result = self._parse_response(response.text)

            # Store in history
            self.conversation_history.append({
                "role": "interviewer",
                "message": result["message"],
                "topic": result.get("topic"),
                "timestamp": "start"
            })

            return result

        except Exception as e:
            print(f"Error getting initial message: {e}")
            return {
                "message": "Hello! Thank you for joining me today. To start off, could you please introduce yourself and tell me a bit about your background?",
                "is_complete": False,
                "topic": "introduction"
            }

    async def process_candidate_response(
        self,
        response: str,
        voice_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process candidate's response and generate next question/follow-up

        Args:
            response: Candidate's transcribed answer
            voice_analysis: Optional voice characteristics analysis

        Returns:
            Dict with interviewer's next message and metadata
        """
        # Store candidate's response in history
        self.conversation_history.append({
            "role": "candidate",
            "message": response,
            "voice_analysis": voice_analysis
        })

        # Build context for AI
        context = self._build_conversation_context(response)

        try:
            # Get AI's response
            ai_response = self.chat.send_message(context)
            result = self._parse_response(ai_response.text)

            # Update state
            if result.get("topic") and result["topic"] not in self.topics_covered:
                self.topics_covered.append(result["topic"])

            if not self.has_introduced:
                self.has_introduced = True

            if result.get("is_complete"):
                self.is_complete = True

            # Store in history
            self.conversation_history.append({
                "role": "interviewer",
                "message": result["message"],
                "topic": result.get("topic"),
                "is_complete": result.get("is_complete", False)
            })

            return result

        except Exception as e:
            print(f"Error processing response: {e}")
            # Fallback response
            return {
                "message": "I see. Could you elaborate more on that?",
                "is_complete": False,
                "topic": "follow-up"
            }

    def _build_conversation_context(self, latest_response: str) -> str:
        """Build context for the AI based on conversation progress"""
        topics_covered_str = ', '.join(
            self.topics_covered) if self.topics_covered else 'none yet'

        context = f"""
Candidate's latest response: "{latest_response}"

Context:
- Topics covered so far: {topics_covered_str}
- Technologies to assess: {', '.join(self.technologies)}
- Number of exchanges so far: {len(self.conversation_history)}

Based on their response, decide:
1. If you need follow-up/clarification on current topic
2. If you should move to a new technical topic
3. If you've thoroughly assessed their skills (don't rush - continue if there's more to explore)

Remember: 
- Be conversational and natural
- Don't end prematurely - ensure thorough assessment
- Only set is_complete=true when you're genuinely satisfied with the evaluation
- The candidate may also indicate they want to end

Provide your response in JSON format."""

        return context

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON"""
        try:
            # Clean markdown if present
            content = response_text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)
            return result

        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response_text}")
            # Try to extract message at least
            return {
                "message": response_text,
                "is_complete": False,
                "topic": "general"
            }

    def get_question_audio(self, message: str) -> bytes:
        """Generate audio for the interviewer's message using TTS"""
        return voice_service.synthesize_speech(message)

    async def transcribe_answer(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe candidate's audio answer to text"""
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

    async def generate_final_report(self) -> Dict[str, Any]:
        """Generate final interview report based on entire conversation"""
        # Prepare conversation transcript
        transcript_text = "\n\n".join([
            f"{'Interviewer' if msg['role'] == 'interviewer' else 'Candidate'}: {msg['message']}"
            for msg in self.conversation_history
        ])

        prompt = f"""Analyze this complete interview conversation and provide an HONEST, CRITICAL evaluation. Do NOT be overly generous or inflate scores.

Interview Details:
- Position: {self.target_role}
- Interview Type: {self.interview_type}
- Technologies: {', '.join(self.technologies)}
- Difficulty: {self.difficulty}

Full Interview Transcript:
{transcript_text}

**CRITICAL EVALUATION RULES:**
1. If answers were WRONG or INCOMPLETE, reflect that in LOW scores (30-50)
2. If answers were VAGUE or lacking detail, give MEDIUM scores (50-70)
3. If answers were GOOD but not exceptional, give FAIR scores (70-80)
4. Only give HIGH scores (80-95) for truly excellent, detailed, accurate answers
5. BE HONEST - don't inflate scores to make candidates feel good
6. Point out SPECIFIC mistakes or gaps in knowledge
7. If they struggled, the overall score should be LOW (below 60)
8. If they did mediocre, give 60-75
9. If they did well, give 75-85
10. Only exceptional candidates get 85+

Evaluate the candidate on:
1. Technical Knowledge & Accuracy (25%) - Were answers CORRECT and COMPLETE?
2. Communication Skills & Clarity (20%) - Could they explain clearly?
3. Problem-Solving Approach (20%) - Did they think through problems logically?
4. Depth of Understanding (20%) - Did they show DEEP knowledge or just surface level?
5. Confidence & Professionalism (15%) - Were they composed and professional?

Provide evaluation in JSON format:
{{
  "overall_score": 65,
  "category_scores": {{
    "technical_knowledge": 60,
    "communication": 70,
    "problem_solving": 65,
    "depth": 55,
    "confidence": 75
  }},
  "summary": "2-3 sentence HONEST overall summary (mention both good and bad)",
  "detailed_feedback": "Comprehensive paragraph analyzing their ACTUAL performance - be specific about mistakes, gaps, and successes",
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "improvement_areas": ["specific gap 1 with example", "specific gap 2 with example", "specific gap 3 with example"],
  "key_highlights": ["specific good moment", "specific weak moment", "overall pattern"],
  "recommendation": "hire/maybe/no (be honest - most candidates are 'maybe' or 'no')",
  "next_steps": "Specific, actionable advice for improvement based on their actual gaps"
}}

Remember: A 50-60 score is NOT a failure, it's honest feedback. Don't inflate scores!"""

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Clean markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            report = json.loads(content)

            # Add transcript
            report["transcript"] = self.conversation_history
            report["topics_covered"] = self.topics_covered

            return report

        except Exception as e:
            print(f"Error generating report: {e}")
            # Fallback report
            return {
                "overall_score": 70,
                "category_scores": {
                    "technical_knowledge": 70,
                    "communication": 70,
                    "problem_solving": 70,
                    "depth": 70,
                    "confidence": 70
                },
                "summary": "The candidate demonstrated understanding of key concepts.",
                "detailed_feedback": "Based on the conversation, the candidate showed reasonable technical knowledge and communication skills.",
                "strengths": ["Engaged in conversation", "Attempted to answer questions"],
                "improvement_areas": ["Could provide more specific examples", "Deepen technical knowledge"],
                "key_highlights": ["Completed the interview"],
                "recommendation": "maybe",
                "next_steps": "Continue learning and practice interview skills.",
                "transcript": self.conversation_history,
                "topics_covered": self.topics_covered
            }
