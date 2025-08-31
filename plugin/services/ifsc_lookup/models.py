from typing import Optional

from pydantic import BaseModel, Field


class IFSCVerificationRequest(BaseModel):
    ifsc: str = Field(..., max_length=11, description="IFSC code to verify")


class IFSCVerificationResponse(BaseModel):
    message: Optional[str] = None
    code: Optional[int] = None
    sub_code: Optional[str] = None
    transaction_id: Optional[str] = None
    MICR: Optional[str] = None
    BRANCH: Optional[str] = None
    ADDRESS: Optional[str] = None
    STATE: Optional[str] = None
    CONTACT: Optional[str] = None
    UPI: Optional[bool] = None
    RTGS: Optional[bool] = None
    CITY: Optional[str] = None
    CENTRE: Optional[str] = None
    DISTRICT: Optional[str] = None
    NEFT: Optional[bool] = None
    IMPS: Optional[bool] = None
    SWIFT: Optional[str] = None
    ISO3166: Optional[str] = None
    BANK: Optional[str] = None
    BANKCODE: Optional[str] = None
    IFSC: Optional[str] = None
