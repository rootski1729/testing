from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class DrivingLicenseVerificationRequest(BaseModel):
    dl_number: str = Field(..., max_length=50, description="Driving License number")
    dob: date = Field(..., description="Date of Birth in YYYY-MM-DD format")


class CovDetail(BaseModel):
    category: Optional[str] = None
    cov: Optional[str] = None
    issue_date: Optional[str] = None


class DrivingLicenseVerificationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    request_id: Optional[str] = None

    # DL details
    id_number: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    relatives_name: Optional[str] = None
    address: Optional[str] = None
    issuing_rto_name: Optional[str] = None
    date_of_issue: Optional[str] = None
    dl_status: Optional[str] = None
    nt_validity_from: Optional[str] = None
    nt_validity_to: Optional[str] = None
    t_validity_from: Optional[str] = None
    t_validity_to: Optional[str] = None

    cov_details: Optional[List[CovDetail]] = None
