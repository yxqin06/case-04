import hashlib
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = None # new
    submission_id: Optional[str] = None # new
  

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v
        
#Good example of inheritance
class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
    @classmethod
    def from_submission(cls, sub: SurveySubmission, ip: str):
        hashed_email = sha256_hash(sub.email)
        hashed_age = sha256_hash(str(sub.age))
        submission_id = sub.submission_id
        if not submission_id:
            now = datetime.utcnow().strftime("%Y%m%d%H")
            submission_id = sha256_hash(hashed_email + now)
        return cls(
            **sub.dict(exclude={"submission_id", "email", "age}),
            email=hashed_email,
            age=hashed_age,
            submission_id=submission_id,
            received_at=datetime.utcnow(),
            ip=ip
        )
