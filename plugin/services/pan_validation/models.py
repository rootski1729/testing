from typing import List, Optional
from pydantic import BaseModel, Field


class PANVerificationRequest(BaseModel):
    pan_number: str = Field(..., min_length=10, max_length=10, description="10-character PAN number")


class PANVerificationResponse(BaseModel):
    # Meta fields
    success: bool = False
    message: Optional[str] = None
    request_id: Optional[str] = None

    # API response fields
    pan_number: Optional[str] = None
    full_name: Optional[str] = None
    full_name_split: Optional[List[str]] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    masked_aadhaar: Optional[str] = None
    aadhaar_linked: Optional[bool] = None

    transaction_id: Optional[str] = None
    sub_code: Optional[str] = None
