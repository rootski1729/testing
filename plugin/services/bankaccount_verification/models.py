from typing import Dict, Optional

from pydantic import BaseModel, Field


class BankAccountVerificationRequest(BaseModel):
    account_number: str = Field(..., max_length=20, description="Bank account number")
    ifsc: str = Field(..., max_length=11, description="Bank IFSC code")
    name: str = Field(..., max_length=255, description="Account holder name")


class NameInformation(BaseModel):
    name_at_bank_cleaned: Optional[str] = None


class BankAccountVerificationResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: Optional[int] = None
    transaction_id: Optional[str] = None

    account_exists: Optional[bool] = None
    name_at_bank: Optional[str] = None
    utr: Optional[str] = None
    amount_deposited: Optional[int] = None

    # Nested response
    name_information: Optional[Dict] = None
