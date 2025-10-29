from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, BinaryIO
import uuid
from datetime import datetime
import json
import re
import google.generativeai as genai

from app.models.resume import Resume
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class ResumeService:
    
    @staticmethod
    def parse_resume_text(file_content: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured information using AI
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Analyze this resume and extract structured information.

Resume Content:
{file_content[:10000]}  # Limit to avoid token limits

Extract the following information and return as JSON:
{{
    "contact_info": {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "+1234567890",
        "location": "City, Country",
        "linkedin": "linkedin.com/in/username",
        "github": "github.com/username",
        "portfolio": "website.com"
    }},
    "summary": "Professional summary or objective",
    "skills": ["skill1", "skill2", "skill3"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, Country",
            "start_date": "Jan 2020",
            "end_date": "Dec 2021",
            "description": "Job description",
            "achievements": ["achievement1", "achievement2"]
        }}
    ],
    "education": [
        {{
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "university": "University Name",
            "location": "City, Country",
            "graduation_date": "2020",
            "gpa": "3.8/4.0"
        }}
    ],
    "certifications": ["certification1", "certification2"],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["tech1", "tech2"],
            "url": "github.com/project"
        }}
    ],
    "achievements": ["achievement1", "achievement2"],
    "languages": ["English", "Spanish"]
}}

Return ONLY valid JSON, no markdown or explanation."""
        
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean markdown
            if content.startswith("```"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            parsed_data = json.loads(content)
            
            # Ensure all required fields exist
            default_structure = {
                "contact_info": {},
                "summary": "",
                "skills": [],
                "experience": [],
                "education": [],
                "certifications": [],
                "projects": [],
                "achievements": [],
                "languages": []
            }
            
            for key, default_value in default_structure.items():
                if key not in parsed_data:
                    parsed_data[key] = default_value
            
            return parsed_data
            
        except Exception as e:
            print(f"Resume parsing error: {e}")
            # Return basic structure with extracted text
            return {
                "contact_info": ResumeService._extract_contact_info(file_content),
                "summary": "",
                "skills": ResumeService._extract_skills(file_content),
                "experience": [],
                "education": [],
                "certifications": [],
                "projects": [],
                "achievements": [],
                "languages": []
            }
    
    
    @staticmethod
    def _extract_contact_info(text: str) -> Dict[str, str]:
        """Fallback: Extract contact info using regex"""
        contact_info = {}
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact_info["email"] = email_match.group()
        
        # Phone
        phone_match = re.search(r'[\+$$]?[1-9][0-9 .\-$$$$]{8,}[0-9]', text)
        if phone_match:
            contact_info["phone"] = phone_match.group()
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact_info["linkedin"] = linkedin_match.group()
        
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github_match:
            contact_info["github"] = github_match.group()
        
        return contact_info
    
    
    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """Fallback: Extract common skills"""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'SQL', 'React', 'Node.js',
            'Django', 'Flask', 'FastAPI', 'MongoDB', 'PostgreSQL', 'AWS',
            'Docker', 'Kubernetes', 'Git', 'Machine Learning', 'AI', 'API'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    
    @staticmethod
    def analyze_resume(parsed_data: Dict[str, Any], target_role: Optional[str] = None) -> Dict[str, Any]:
        """
        AI-powered comprehensive resume analysis
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        target_context = f"\nTarget Role: {target_role}" if target_role else ""
        
        prompt = f"""Analyze this resume comprehensively and provide detailed feedback.

Resume Data:
{json.dumps(parsed_data, indent=2)}
{target_context}

Provide analysis in JSON format:
{{
    "ats_score": <0-100 integer>,
    "overall_rating": "<excellent|good|average|needs_improvement>",
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2", "weakness3"],
    "missing_sections": ["section1", "section2"],
    "skills_analysis": {{
        "technical_skills": ["skill1", "skill2"],
        "soft_skills": ["skill1", "skill2"],
        "missing_skills": ["skill1", "skill2"],
        "skill_level": "junior|mid|senior"
    }},
    "experience_analysis": {{
        "total_years": 3,
        "relevant_experience": true,
        "career_progression": "good|average|poor",
        "gaps": []
    }},
    "education_analysis": {{
        "relevance": "high|medium|low",
        "completeness": true,
        "recommendations": []
    }},
    "recommendations": [
        "recommendation1",
        "recommendation2",
        "recommendation3"
    ],
    "keyword_match": {{
        "matched_keywords": ["keyword1", "keyword2"],
        "missing_keywords": ["keyword1", "keyword2"],
        "match_percentage": 75
    }},
    "detailed_feedback": "Comprehensive paragraph feedback about the resume..."
}}

Return ONLY valid JSON."""
        
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            analysis = json.loads(content)
            
            # Ensure ATS score is valid
            if "ats_score" in analysis:
                analysis["ats_score"] = max(0, min(100, int(analysis["ats_score"])))
            else:
                analysis["ats_score"] = ResumeService._calculate_ats_score(parsed_data)
            
            return analysis
            
        except Exception as e:
            print(f"Analysis error: {e}")
            # Fallback analysis
            return {
                "ats_score": ResumeService._calculate_ats_score(parsed_data),
                "overall_rating": "average",
                "strengths": ["Resume submitted for review"],
                "weaknesses": ["Detailed analysis pending"],
                "missing_sections": [],
                "skills_analysis": {
                    "technical_skills": parsed_data.get("skills", []),
                    "soft_skills": [],
                    "missing_skills": [],
                    "skill_level": "mid"
                },
                "experience_analysis": {
                    "total_years": len(parsed_data.get("experience", [])),
                    "relevant_experience": True,
                    "career_progression": "good",
                    "gaps": []
                },
                "education_analysis": {
                    "relevance": "medium",
                    "completeness": True,
                    "recommendations": []
                },
                "recommendations": [
                    "Add more quantifiable achievements",
                    "Include relevant keywords",
                    "Highlight technical skills"
                ],
                "keyword_match": {
                    "matched_keywords": [],
                    "missing_keywords": [],
                    "match_percentage": 50
                },
                "detailed_feedback": "Resume analysis completed. Consider adding more specific details and measurable achievements."
            }
    
    
    @staticmethod
    def _calculate_ats_score(parsed_data: Dict[str, Any]) -> int:
        """Calculate basic ATS score based on resume completeness"""
        score = 0
        
        # Contact info (20 points)
        contact = parsed_data.get("contact_info", {})
        if contact.get("email"):
            score += 5
        if contact.get("phone"):
            score += 5
        if contact.get("linkedin"):
            score += 5
        if contact.get("github"):
            score += 5
        
        # Skills (20 points)
        skills = parsed_data.get("skills", [])
        if len(skills) >= 5:
            score += 20
        elif len(skills) >= 3:
            score += 15
        elif len(skills) >= 1:
            score += 10
        
        # Experience (30 points)
        experience = parsed_data.get("experience", [])
        if len(experience) >= 3:
            score += 30
        elif len(experience) >= 2:
            score += 20
        elif len(experience) >= 1:
            score += 15
        
        # Education (15 points)
        education = parsed_data.get("education", [])
        if len(education) >= 1:
            score += 15
        
        # Projects (10 points)
        projects = parsed_data.get("projects", [])
        if len(projects) >= 2:
            score += 10
        elif len(projects) >= 1:
            score += 5
        
        # Certifications (5 points)
        certifications = parsed_data.get("certifications", [])
        if len(certifications) >= 1:
            score += 5
        
        return min(100, score)
    
    
    @staticmethod
    def get_resume(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        """Get resume by ID"""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            raise NotFoundException("Resume not found")
        
        return resume
    
    
    @staticmethod
    def get_user_resumes(db: Session, user_id: uuid.UUID) -> List[Resume]:
        """Get all resumes for a user"""
        return db.query(Resume).filter(
            Resume.user_id == user_id
        ).order_by(Resume.created_at.desc()).all()
    
    
    @staticmethod
    def set_primary_resume(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID):
        """Set a resume as primary"""
        # Unset all primary resumes
        db.query(Resume).filter(Resume.user_id == user_id).update({"is_primary": False})
        
        # Set new primary
        resume = ResumeService.get_resume(db, resume_id, user_id)
        resume.is_primary = True
        db.commit()
    
    
    @staticmethod
    def delete_resume(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID):
        """Delete a resume"""
        resume = ResumeService.get_resume(db, resume_id, user_id)
        
        # TODO: Delete file from Supabase storage
        
        db.delete(resume)
        db.commit()
