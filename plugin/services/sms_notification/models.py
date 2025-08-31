# models.py
from typing import Optional

from pydantic import BaseModel, Field


class SMSRequest(BaseModel):
    plugin_uid: str = Field(..., description="UID of the plugin to use")
    mobile: str = Field(..., description="Recipient mobile number (without +91)")
    text: str = Field(..., description="Message content")
    senderName: str = Field(..., description="Sender ID approved on DLT")
    messageType: int = Field(0, description="0 - English, 1 - Flash, 2 - Unicode")
    surl: int = Field(0, description="0 - Do not shorten URL, 1 - Shorten URL")


class SMSResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    code: Optional[int] = None
