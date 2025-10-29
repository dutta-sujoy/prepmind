from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users
from app.api.v1.endpoints import interview
from app.api.v1.endpoints import interview_ws
from app.api.v1.endpoints import resume  # Add this line

__all__ = ["auth", "users", "interview", "interview_ws", "resume"]
