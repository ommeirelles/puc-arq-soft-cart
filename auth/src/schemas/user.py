from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    """
    Payload to register a new user
    """
    name: str = Field(..., min_length=1, description="The user full name")
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="The user email")
    password: str = Field(..., min_length=1, description="The user password")

class User(BaseModel):
    """
    User info
    """
    id: int = Field(..., description="The user ID")
    name: str = Field(..., description="The user full name")
    email: str = Field(..., description="The user email")
