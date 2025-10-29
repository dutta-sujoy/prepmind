from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import json
import google.generativeai as genai

from app.models.interview import Interview, InterviewResult
from app.models.resume import Resume
from app.schemas.interview import InterviewCreate
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class InterviewService:
    
    @staticmethod
    def generate_questions(
        interview_type: str,
        target_role: str,
        technologies: List[str],
        difficulty: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate interview questions using Gemini AI"""
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt
        prompt = f"""Generate {num_questions} {interview_type} interview questions for a {target_role} position.

Technologies to focus on: {', '.join(technologies)}
Difficulty level: {difficulty}

Requirements:
1. Questions should be specific to the technologies mentioned
2. Mix of theoretical and practical questions
3. Progressive difficulty
4. Include follow-up scenarios
5. Test real-world problem-solving

Return ONLY a valid JSON array with this exact structure (no markdown, no explanation):
[
  {{
    "id": 1,
    "text": "question text here",
    "category": "category name",
    "difficulty": "{difficulty}",
    "expected_points": ["point1", "point2", "point3"]
  }}
]"""
        
        try:
            # Generate questions
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            # Remove markdown if present
            if content.startswith("```json"):
                # remove the opening ```json (and any immediate newline)
                content = content[len("```json"):].lstrip("\n")
            if content.startswith("```"):
                # remove a generic opening ```
                content = content[len("```"):].lstrip("\n")
            if content.endswith("```"):
                # remove a trailing ```
                content = content[:-len("```")].rstrip("\n")
            
            content = content.strip()
            
            questions = json.loads(content)
            
            # Validate and ensure correct number
            if not isinstance(questions, list):
                raise ValueError("Response is not a list")
            
            # Ensure IDs are sequential
            for i, q in enumerate(questions, 1):
                q["id"] = i
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Failed to generate questions: {e}")
            return InterviewService._get_fallback_questions(interview_type, num_questions)
    
    
    @staticmethod
    def _get_fallback_questions(interview_type: str, num_questions: int) -> List[Dict[str, Any]]:
        """Fallback questions if AI generation fails"""
        
        fallback_questions = {
            "technical": [
                {
                    "id": 1,
                    "text": "Explain the concept of closures in JavaScript with an example.",
                    "category": "JavaScript Fundamentals",
                    "difficulty": "medium",
                    "expected_points": ["Function scope", "Lexical environment", "Practical use cases"]
                },
                {
                    "id": 2,
                    "text": "What is the difference between SQL and NoSQL databases? When would you use each?",
                    "category": "Databases",
                    "difficulty": "medium",
                    "expected_points": ["Schema differences", "Scalability", "Use cases"]
                },
                {
                    "id": 3,
                    "text": "Explain REST API principles and best practices.",
                    "category": "APIs",
                    "difficulty": "medium",
                    "expected_points": ["HTTP methods", "Statelessness", "Resource naming"]
                },
                {
                    "id": 4,
                    "text": "What is the Virtual DOM in React and how does it improve performance?",
                    "category": "React",
                    "difficulty": "medium",
                    "expected_points": ["DOM manipulation", "Diffing algorithm", "Performance benefits"]
                },
                {
                    "id": 5,
                    "text": "Describe the SOLID principles in object-oriented programming.",
                    "category": "OOP",
                    "difficulty": "hard",
                    "expected_points": ["Single Responsibility", "Open/Closed", "Liskov Substitution"]
                }
            ],
            "hr": [
                {
                    "id": 1,
                    "text": "Tell me about yourself and your background.",
                    "category": "Introduction",
                    "difficulty": "easy",
                    "expected_points": ["Education", "Experience", "Motivation"]
                },
                {
                    "id": 2,
                    "text": "Why do you want to work for our company?",
                    "category": "Motivation",
                    "difficulty": "easy",
                    "expected_points": ["Company research", "Alignment with goals", "Interest"]
                },
                {
                    "id": 3,
                    "text": "Describe a challenging project you worked on and how you overcame obstacles.",
                    "category": "Problem Solving",
                    "difficulty": "medium",
                    "expected_points": ["Situation", "Action", "Result"]
                },
                {
                    "id": 4,
                    "text": "How do you handle conflicts in a team?",
                    "category": "Teamwork",
                    "difficulty": "medium",
                    "expected_points": ["Communication", "Compromise", "Resolution"]
                },
                {
                    "id": 5,
                    "text": "Where do you see yourself in 5 years?",
                    "category": "Career Goals",
                    "difficulty": "easy",
                    "expected_points": ["Growth mindset", "Learning goals", "Career path"]
                }
            ]
        }
        
        questions = fallback_questions.get(interview_type, fallback_questions["technical"])
        return questions[:num_questions]
    
    
    @staticmethod
    def create_interview(db: Session, user_id: uuid.UUID, interview_data: InterviewCreate) -> Interview:
        """Create a new interview with AI-generated questions"""
        
        # Generate questions using AI
        questions = InterviewService.generate_questions(
            interview_type=interview_data.interview_type,
            target_role=interview_data.target_role,
            technologies=interview_data.technologies,
            difficulty=interview_data.difficulty,
            num_questions=interview_data.num_questions
        )
        
        # Create interview
        interview = Interview(
            user_id=user_id,
            interview_type=interview_data.interview_type,
            target_role=interview_data.target_role,
            technologies=interview_data.technologies,
            difficulty=interview_data.difficulty,
            num_questions=interview_data.num_questions,
            questions=questions,
            status="draft"
        )
        
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        return interview
    
    
    @staticmethod
    def get_interview(db: Session, interview_id: uuid.UUID, user_id: uuid.UUID) -> Interview:
        """Get interview by ID"""
        interview = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.user_id == user_id
        ).first()
        
        if not interview:
            raise NotFoundException("Interview not found")
        
        return interview
    
    
    @staticmethod
    def get_user_interviews(db: Session, user_id: uuid.UUID, status: str = None) -> List[Interview]:
        """Get all interviews for a user"""
        query = db.query(Interview).filter(Interview.user_id == user_id)
        
        if status:
            query = query.filter(Interview.status == status)
        
        return query.order_by(Interview.created_at.desc()).all()
    
    
    @staticmethod
    def delete_interview(db: Session, interview_id: uuid.UUID, user_id: uuid.UUID):
        """Delete an interview"""
        interview = InterviewService.get_interview(db, interview_id, user_id)
        
        if interview.status != "draft":
            raise BadRequestException("Can only delete draft interviews")
        
        db.delete(interview)
        db.commit()
    
    
    @staticmethod
    def get_user_resume(db: Session, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get user's primary resume data"""
        resume = db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.is_primary == True
        ).first()
        
        if resume and resume.parsed_data:
            return resume.parsed_data
        
        return {}
