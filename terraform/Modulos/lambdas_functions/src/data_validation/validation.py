from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime   

class ProjectRaw(BaseModel):
    ##TODO: Ver que campos son obligatorios y cuales no

    project_id: str
    name_project: str
    start_date: Optional[str]
    completion_date: Optional[str]
    country: Optional[str]
    location: Optional[str]
    client_name: Optional[str]
    value_contract: Optional[str]
    currency: Optional[str]
    name_consultant: Optional[str]
    description: Optional[str]
    processing_timestamp: Optional[datetime] 

    @validator('project_id', 'name_project', pre=True)
    def must_not_be_empty(cls, value):
        if not value or value.strip() == "":
            raise ValueError("Required field is empty")
        return value
