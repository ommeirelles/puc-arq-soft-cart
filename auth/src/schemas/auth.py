from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """
    Login payload
    """
    email: str = Field(..., description="The user email")
    password: str = Field(..., description="The user password")

class LoginResponse(BaseModel):
    """
    Login response carrying the session token
    """
    token: str = Field(..., description="The session token")
