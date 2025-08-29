from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MobileToVehicleRCRequest(BaseModel):
    mobile_number: str = Field(..., max_length=15, description="Mobile number to fetch Vehicle RC")


class MobileToVehicleRCResponse(BaseModel):
    success: bool
    message: str
    code: Optional[int] = None
    timestamp: Optional[int] = None
    transaction_id: Optional[str] = None
    sub_code: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
