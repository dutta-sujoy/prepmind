from fastapi import APIRouter, Depends, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from app.services.storage_service import storage_service  # Add this import


from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeResponse,
    ResumeListItem,
    ResumeAnalysis
)
from app.schemas.common import ResponseBase
from app.services.resume_service import ResumeService
from app.utils.file_parser import extract_text_from_file
from app.core.exceptions import BadRequestException

router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


from app.services.storage_service import storage_service  # Add this import

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    is_primary: bool = False,
    analyze: bool = True,
    target_role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze resume"""
    
    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower()
    if f".{file_ext}" not in ALLOWED_EXTENSIONS:
        raise BadRequestException(
            f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise BadRequestException(
            f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    if file_size == 0:
        raise BadRequestException("File is empty")
    
    # Extract text from file
    print(f"Extracting text from {file.filename}...")
    extracted_text = extract_text_from_file(file_content, file.content_type)
    
    if not extracted_text:
        raise BadRequestException("Could not extract text from file")
    
    print(f"Extracted {len(extracted_text)} characters")
    
    # Parse resume
    print("Parsing resume with AI...")
    parsed_data = ResumeService.parse_resume_text(extracted_text)
    
    # Calculate ATS score
    ats_score = ResumeService._calculate_ats_score(parsed_data)
    
    # Perform analysis if requested
    analysis_result = None
    if analyze:
        print("Analyzing resume...")
        analysis_result = ResumeService.analyze_resume(parsed_data, target_role)
        ats_score = analysis_result.get("ats_score", ats_score)
    
    # Upload file to Supabase Storage
    print("Uploading to Supabase Storage...")
    try:
        file_url = storage_service.upload_resume(
            file_content=file_content,
            user_id=current_user.id,
            filename=file.filename
        )
        print(f"✅ File uploaded to: {file_url}")
    except Exception as e:
        print(f"❌ Storage upload failed: {e}")
        # Fallback to local path if storage fails
        file_url = f"/storage/resumes/{current_user.id}/{uuid.uuid4()}.{file_ext}"
    
    # Create resume record
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_url=file_url,
        file_type=file.content_type or f"application/{file_ext}",
        file_size=file_size,
        is_primary=is_primary,
        parsed_data=parsed_data,
        ats_score=ats_score,
        analysis_result=analysis_result,
        raw_text=extracted_text
    )
    
    # If setting as primary, unset others
    if is_primary:
        db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_primary": False})
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    print(f"✅ Resume saved to database: {resume.id}")
    
    return resume



@router.get("/list", response_model=List[ResumeListItem])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resumes for the current user
    """
    resumes = ResumeService.get_user_resumes(db, current_user.id)
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed resume information including parsed data and analysis
    """
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    return resume


@router.post("/{resume_id}/analyze", response_model=ResumeResponse)
async def analyze_resume(
    resume_id: uuid.UUID,
    target_role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Re-analyze an existing resume with optional target role
    
    Useful for:
    - Getting analysis for different roles
    - Updating analysis with new AI model
    - Re-evaluating after edits
    """
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    if not resume.parsed_data:
        raise BadRequestException("Resume has not been parsed yet")
    
    print(f"Re-analyzing resume {resume_id}...")
    analysis = ResumeService.analyze_resume(resume.parsed_data, target_role)
    
    # Update resume
    resume.analysis_result = analysis
    resume.ats_score = analysis.get("ats_score", resume.ats_score)
    resume.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(resume)
    
    return resume


@router.post("/{resume_id}/set-primary", response_model=ResponseBase)
async def set_primary_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set a resume as primary
    
    Primary resume is used for:
    - Interview preparation
    - Skill analysis
    - Career recommendations
    """
    ResumeService.set_primary_resume(db, resume_id, current_user.id)
    
    return ResponseBase(
        success=True,
        message="Resume set as primary"
    )


@router.delete("/{resume_id}", response_model=ResponseBase)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    # Delete file from storage
    try:
        storage_service.delete_resume(resume.file_url)
        print(f"✅ File deleted from storage: {resume.file_url}")
    except Exception as e:
        print(f"⚠️ Failed to delete file from storage: {e}")
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return ResponseBase(
        success=True,
        message="Resume deleted successfully"
    )


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get download URL for resume
    """
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    return {
        "resume_id": str(resume.id),
        "file_name": resume.file_name,
        "download_url": resume.file_url,
        "file_size": resume.file_size
    }


@router.get("/{resume_id}/analysis", response_model=dict)
async def get_resume_analysis(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis of a resume
    
    Returns comprehensive feedback including:
    - ATS score
    - Strengths and weaknesses
    - Skills analysis
    - Experience evaluation
    - Recommendations
    """
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    if not resume.analysis_result:
        raise BadRequestException("Resume has not been analyzed yet")
    
    return {
        "resume_id": str(resume.id),
        "file_name": resume.file_name,
        "analysis": resume.analysis_result,
        "ats_score": resume.ats_score,
        "analyzed_at": resume.updated_at
    }



from pydantic import BaseModel

# Add this schema near the top
class JobComparisonRequest(BaseModel):
    job_description: str
    job_title: str

# Update the compare endpoint
@router.post("/{resume_id}/compare", response_model=dict)
async def compare_with_job_description(
    resume_id: uuid.UUID,
    request: JobComparisonRequest,  # Changed from individual parameters
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare resume with a job description"""
    
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    if not resume.parsed_data:
        raise BadRequestException("Resume has not been parsed yet")
    
    import google.generativeai as genai
    import json
    from app.config import settings
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""Compare this resume with the job description and provide match analysis.

Resume Data:
{json.dumps(resume.parsed_data, indent=2)}

Job Title: {request.job_title}
Job Description:
{request.job_description}

Provide analysis in JSON:
{{
    "match_percentage": <0-100>,
    "matched_keywords": ["keyword1", "keyword2"],
    "missing_keywords": ["keyword1", "keyword2"],
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "experience_match": "high|medium|low",
    "education_match": "high|medium|low",
    "recommendations": ["rec1", "rec2", "rec3"],
    "tailoring_suggestions": ["suggestion1", "suggestion2"],
    "summary": "Brief summary of match quality"
}}

Return ONLY valid JSON."""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Remove surrounding triple backticks and optional language markers (e.g. ```json\n ... ```).
        # Use regex to safely strip leading/trailing fences and any optional language token.
        import re
        # Strip leading fences like ``` or ```lang (optionally preceded by whitespace)
        content = re.sub(r'^\s*```(?:[^\n]*)\n?', '', content)
        # Strip trailing fences like ``` optionally followed by whitespace/newline
        content = re.sub(r'\n?```\s*$', '', content)
        content = content.strip()
        
        comparison = json.loads(content)
        
        return {
            "resume_id": str(resume.id),
            "job_title": request.job_title,
            "comparison": comparison
        }
        
    except Exception as e:
        print(f"Comparison error: {e}")
        raise BadRequestException("Failed to compare resume with job description")
