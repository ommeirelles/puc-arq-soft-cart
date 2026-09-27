from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """
    Login payload
    """
    username: str = Field(..., description="The username")
    password: str = Field(..., description="The password")

class LoginResponse(BaseModel):
    """
    Login response carrying the session token
    """
    token: str = Field(..., description="The session token")
