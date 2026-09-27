from pydantic import BaseModel, Field

class UserName(BaseModel):
    """
    Name of an user
    """
    firstname: str = Field(..., description="The user first name")
    lastname: str = Field(..., description="The user last name")

class User(BaseModel):
    """
    User info from the external store API
    """
    id: int = Field(..., description="The user ID")
    email: str = Field(..., description="The user email")
    username: str = Field(..., description="The username")
    name: UserName = Field(..., description="The user name")
    phone: str = Field(..., description="The user phone")
