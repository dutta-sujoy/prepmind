from typing import List, Dict, Any, Optional
import json
import google.generativeai as genai
from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class RealTimeInterviewAgent:
    """
    Real-time interview agent using direct Gemini API
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
        self.is_complete = False
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create system context
        self.system_context = self._create_system_context()
    
    
    def _create_system_context(self) -> str:
        """Create system context based on interview details"""
        
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

Your responsibilities:
1. Evaluate answers objectively based on technical accuracy, communication clarity, and depth
2. Provide constructive, specific feedback
3. Score answers from 1-10
4. Be professional and encouraging

Scoring Guidelines:
- 1-3: Poor understanding
- 4-5: Below average, needs improvement
- 6-7: Average, room for growth
- 8-9: Good understanding and application
- 10: Excellent depth and clarity"""
    
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question"""
        if self.current_question_index < self.total_questions:
            return self.questions[self.current_question_index]
        return None
    
    
    def has_more_questions(self) -> bool:
        """Check if there are more questions"""
        return self.current_question_index < self.total_questions
    
    
    async def evaluate_answer(self, answer: str, time_taken: int = 0) -> Dict[str, Any]:
        """Evaluate candidate's answer using Gemini AI"""
        
        current_question = self.questions[self.current_question_index]
        
        # Create evaluation prompt
        prompt = f"""{self.system_context}

Question #{self.current_question_index + 1}: {current_question['text']}

Expected Key Points: {', '.join(current_question['expected_points'])}
Difficulty: {current_question['difficulty']}

Candidate's Answer:
"{answer}"

Time taken: {time_taken} seconds

Evaluate this answer and provide a JSON response:
{{
    "score": <integer 1-10>,
    "feedback": "<2-3 sentences of constructive feedback>",
    "strengths": ["specific strength 1", "specific strength 2"],
    "improvements": ["specific area 1", "specific area 2"],
    "follow_up": null
}}

Return ONLY valid JSON, no markdown."""
        
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
            
            evaluation = json.loads(content)
            
            # Validate score
            if not isinstance(evaluation.get("score"), (int, float)):
                raise ValueError("Invalid score")
            
            evaluation["score"] = max(1, min(10, int(evaluation["score"])))
            
        except Exception as e:
            print(f"Evaluation error: {e}")
            # Fallback evaluation
            score = self._calculate_fallback_score(answer, current_question)
            evaluation = {
                "score": score,
                "feedback": "Good effort. Your answer shows understanding, but could be more detailed.",
                "strengths": ["Demonstrated basic understanding"],
                "improvements": ["Provide more specific examples"],
                "follow_up": None
            }
        
        # Store score and feedback
        self.scores.append(evaluation["score"])
        self.feedback_history.append({
            "question_number": self.current_question_index + 1,
            "question_text": current_question["text"],
            "answer": answer,
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
            "time_taken": time_taken
        })
        
        # Move to next question
        self.current_question_index += 1
        
        # Check if complete
        if self.current_question_index >= self.total_questions:
            self.is_complete = True
        
        return evaluation
    
    
    def _calculate_fallback_score(self, answer: str, question: Dict[str, Any]) -> int:
        """Calculate basic score based on answer characteristics"""
        score = 5
        
        word_count = len(answer.split())
        if word_count < 20:
            score -= 1
        elif word_count > 50:
            score += 1
        
        # Check expected points
        expected_points = question.get("expected_points", [])
        answer_lower = answer.lower()
        
        matches = sum(1 for point in expected_points if any(
            keyword.lower() in answer_lower 
            for keyword in point.split()[:3]
        ))
        
        if matches > 0:
            score += min(2, matches)
        
        return max(1, min(10, score))
    
    
    async def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        if not self.scores:
            return {
                "overall_score": 0,
                "summary": "No answers evaluated.",
                "detailed_feedback": {},
                "strengths": [],
                "improvement_areas": [],
                "transcript": []
            }
        
        overall_score = int(sum(self.scores) / len(self.scores))
        
        # Create summary prompt
        prompt = f"""{self.system_context}

Interview Completed
Overall Score: {overall_score}/10
Total Questions: {self.total_questions}

Performance Data:
{json.dumps(self.feedback_history, indent=2)}

Generate a comprehensive summary as JSON:
{{
    "summary": "<2-3 sentence overall assessment>",
    "detailed_feedback": {{
        "technical_depth": <1-10>,
        "communication": <1-10>,
        "problem_solving": <1-10>,
        "confidence": <1-10>
    }},
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "improvement_areas": ["area 1", "area 2", "area 3"],
    "recommendation": "<hire|consider|not recommended>",
    "next_steps": "<advice for candidate>"
}}

Return ONLY valid JSON."""
        
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
            
        except Exception as e:
            print(f"Report generation error: {e}")
            report = {
                "summary": f"Completed {self.interview_type} interview with overall score of {overall_score}/10.",
                "detailed_feedback": {
                    "technical_depth": overall_score,
                    "communication": overall_score,
                    "problem_solving": overall_score,
                    "confidence": overall_score
                },
                "strengths": ["Completed all questions"],
                "improvement_areas": ["Continue practicing"],
                "recommendation": "consider" if overall_score >= 6 else "not recommended",
                "next_steps": "Keep practicing and review weak areas"
            }
        
        return {
            "overall_score": overall_score,
            "summary": report.get("summary", ""),
            "detailed_feedback": report.get("detailed_feedback", {}),
            "strengths": report.get("strengths", []),
            "improvement_areas": report.get("improvement_areas", []),
            "recommendation": report.get("recommendation", ""),
            "next_steps": report.get("next_steps", ""),
            "transcript": self.feedback_history
        }
    
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        return {
            "current_question": self.current_question_index + 1,
            "total_questions": self.total_questions,
            "completed": self.current_question_index,
            "remaining": self.total_questions - self.current_question_index,
            "is_complete": self.is_complete
        }
