from pydantic import BaseModel, Field
from typing import Optional


class PANEligibilityRequest(BaseModel):
    plugin_uid: str = Field(..., description="Unique identifier for the plugin")
    pan: str = Field(..., description="10-character PAN number")
    mobile: Optional[str] = Field(None, description="10-digit mobile number")
    use_cache: Optional[bool] = True
    cache_validity_minutes: Optional[int] = 10


class PANEligibilityResponse(BaseModel):
    success: bool
    message: Optional[str] = None

    verification_status: Optional[str] = Field(
        None, description="Standardized verification status"
    )
    
    verified_at: Optional[str] = None

    agent_enum: Optional[str] = None
    error_code: Optional[str] = None
    error: Optional[str] = None
    is_cached_response: Optional[bool] = None
