from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VehicleRCVerificationRequest(BaseModel):
    rc_number: str


class VehicleRCVerificationResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    transaction_id: Optional[str] = None
    sub_code: Optional[str] = None

    registration_number: Optional[str] = None
    vehicle_registration_date: Optional[datetime] = None
    user: Optional[str] = None
    father_name: Optional[str] = None
    present_address: Optional[str] = None
    permanent_address: Optional[str] = None
    mobile_number: Optional[str] = None
    vehicle_category: Optional[str] = None
    vehicle_chassis_number: Optional[str] = None
    vehicle_engine_number: Optional[str] = None
    maker_description: Optional[str] = None
    model: Optional[str] = None
    body_type: Optional[str] = None
    vehicle_fuel_type: Optional[str] = None
    vehicle_color: Optional[str] = None
    norms_type: Optional[str] = None
    fit_up_to: Optional[datetime] = None
    financer: Optional[str] = None
    insurance_company: Optional[str] = None
    last_policy_number: Optional[str] = None
    insurance_upto: Optional[datetime] = None
    manufactured_month_year: Optional[str] = None
    registered_at: Optional[str] = None
    latest_by: Optional[str] = None

    less_info: Optional[bool] = None
    noc_details: Optional[str] = None
    owner_sr: Optional[str] = None

    permit_number: Optional[str] = None
    permit_issue_date: Optional[datetime] = None
    permit_valid_from: Optional[datetime] = None
    permit_valid_upto: Optional[datetime] = None
    permit_type: Optional[str] = None
    national_permit_number: Optional[str] = None
    national_permit_issued_by: Optional[str] = None
    national_permit_valid_from: Optional[datetime] = None
    national_permit_valid_upto: Optional[datetime] = None

    blacklist_status: Optional[str] = None
    rc_status: Optional[str] = None
    puc_number: Optional[str] = None
    puc_valid_upto: Optional[datetime] = None
    masked_aadhaar_number: Optional[str] = None
    masked_mobile_number: Optional[str] = None
