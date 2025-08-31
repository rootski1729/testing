from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AadhaarOTPGenerateRequest(BaseModel):
    aadhaar_number: str = Field(..., description="12-digit Aadhaar number")
    consent: str = Field("Y", description="Consent flag (Y/N)")
    purpose: str = Field("ForKYC", description="Purpose of Aadhaar verification")


class AadhaarOTPGenerateResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    code: Optional[int] = None
    reference_id: Optional[str] = None
    transaction_id: Optional[str] = None
    sub_code: Optional[str] = None


class AadhaarOTPVerifyRequest(BaseModel):
    otp: str = Field(..., description="OTP received on registered mobile")
    reference_id: str = Field(..., description="Reference ID from generate-otp")
    consent: str = Field("Y", description="Consent flag (Y/N)")
    purpose: str = Field("ForKYC", description="Purpose of Aadhaar verification")
    mobile_number: Optional[str] = Field(
        None, description="Mobile number used for Aadhaar verification"
    )
    generate_pdf: bool = False


class AadhaarVerificationResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    code: Optional[int] = None
    aadhaar_number: Optional[str] = None
    masked_number: Optional[str] = None
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    photo: Optional[str] = None
    document_pdf: Optional[str] = None
    aadhaar_linked_mobile_match: Optional[str] = None
    transaction_id: Optional[str] = None
    sub_code: Optional[str] = None
