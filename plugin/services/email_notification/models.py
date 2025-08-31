from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class EmailRequest(BaseModel):
    plugin_uid: str = Field(..., description="UID of the plugin to use for sending email")
    from_email: str = Field(..., alias="from_email", description="Sender email in format: 'Acme <onboarding@resend.dev>'")
    to: List[EmailStr] = Field(..., description="Recipient email addresses")
    subject: str = Field(..., description="Email subject")
    html: str = Field(..., description="HTML email content")


class EmailResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    id: Optional[str] = None
