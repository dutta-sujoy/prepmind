from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    resume,
    interview,
    interview_ws,
    roadmap,
    dashboard,
    platforms,
    jobs,
    projects,
    cover_letter,
    companies,
    notifications,
    analytics,
    utils,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(resume.router, prefix="/resumes", tags=["Resumes"])

api_router.include_router(interview.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(interview_ws.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Career Roadmap"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["Platform Sync"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(cover_letter.router, prefix="/cover-letter", tags=["Cover Letter"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(utils.router, prefix="/utils", tags=["Utilities"])
