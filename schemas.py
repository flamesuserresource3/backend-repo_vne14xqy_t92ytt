from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

# Portfolio-specific schemas

class Project(BaseModel):
    """
    Portfolio projects
    Collection name: "project"
    """
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Short description of the project")
    tags: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="Live demo URL")
    repo: Optional[str] = Field(None, description="Source code repository URL")
    thumbnail: Optional[str] = Field(None, description="Image URL for the project card")

class Message(BaseModel):
    """
    Contact messages
    Collection name: "message"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    message: str = Field(..., min_length=5, max_length=2000, description="Message body")

# Example additional schemas (kept minimal for reference)
class User(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True
