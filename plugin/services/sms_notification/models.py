# models.py
from pydantic import BaseModel, Field
from typing import Optional


class SMSRequest(BaseModel):
    mobile: str = Field(..., description="Recipient mobile number (without +91)")
    text: str = Field(..., description="Message content")
    senderName: str = Field(..., description="Sender ID approved on DLT")
    messageType: int = Field(0, description="0 - English, 1 - Flash, 2 - Unicode")
    surl: int = Field(0, description="0 - Do not shorten URL, 1 - Shorten URL")


class SMSResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    code: Optional[int] = None
    response_id: Optional[str] = None
