from app.models.user import User, UserPreference
from app.models.token import RefreshToken
from app.models.resume import Resume
from app.models.interview import Interview, InterviewResult
from app.models.notification import Notification

# Import other models as we create them
# from app.models.roadmap import CareerRoadmap, RoadmapMilestone
# from app.models.progress import SkillProgress
# from app.models.project import Project
# from app.models.cover_letter import CoverLetter
# from app.models.job import Job, JobBookmark, JobApplication, JobAlert
# from app.models.company import Company, CompanyQuestion, UserCompanyProgress
# from app.models.analytics import UserAnalytics
# from app.models.feedback import Feedback

__all__ = [
    "User",
    "UserPreference",
    "RefreshToken",
    "Resume",
    "Interview",
    "InterviewResult",
    "Notification",
]
