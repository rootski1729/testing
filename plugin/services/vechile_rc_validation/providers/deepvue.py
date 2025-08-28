import httpx
from typing import Dict, Any, TYPE_CHECKING
from .abc import AbstractVehicleRCVerificationProvider
from plugin.utils.deepvue_auth import DeepvueAuth
from ..vechile_rc_serializer import VehicleRCVerificationResponseSerializer,VehicleRCVerificationRequestSerializer  

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractVehicleRCVerificationProvider):

    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.auth = DeepvueAuth(client_id, client_secret)

    def verify_rc(
        self, plugin: "Plugin", request: VehicleRCVerificationRequestSerializer
    ) -> VehicleRCVerificationResponseSerializer:
        try:
            rc_number = request.validated_data["rc_number"]
            result = self.auth.make_request(
                "GET",
                "/v1/verification/rc-advanced",
                params={"rc_number": rc_number},
            )

            data = result.get("data", {}) or {}

        
            response_payload = {
                "success": (result.get("sub_code") == "SUCCESS"),
                "message": result.get("message"),
                "transaction_id": result.get("transaction_id"),
                "sub_code": result.get("sub_code"),
                "provider": "deepvue",
                "registration_number": data.get("rc_number"),
                "vehicle_registration_date": data.get("registration_date"),
                "user": data.get("owner_name"),
                "father_name": data.get("father_name"),
                "present_address": data.get("present_address"),
                "permanent_address": data.get("permanent_address"),
                "mobile_number": data.get("mobile_number"),
                "vehicle_category": data.get("vehicle_category"),
                "vehicle_chassis_number": data.get("vehicle_chasi_number"),
                "vehicle_engine_number": data.get("vehicle_engine_number"),
                "maker_description": data.get("maker_description"),
                "maker_model": data.get("maker_model"),
                "body_type": data.get("body_type"),
                "vehicle_fuel_type": data.get("fuel_type"),
                "vehicle_color": data.get("color"),
                "norms_type": data.get("norms_type"),
                "fit_up_to": data.get("fit_up_to"),
                "financer": data.get("financer"),
                "financed": data.get("financed"),
                "insurance_company": data.get("insurance_company"),
                "insurance_policy_number": data.get("insurance_policy_number"),
                "insurance_upto": data.get("insurance_upto"),
                "manufacturing_date": data.get("manufacturing_date"),
                "manufacturing_date_formatted": data.get("manufacturing_date_formatted"),
                "registered_at": data.get("registered_at"),
                "latest_by": data.get("latest_by"),
                "less_info": data.get("less_info"),
                "tax_upto": data.get("tax_upto"),
                "tax_paid_upto": data.get("tax_paid_upto"),
                "cubic_capacity": data.get("cubic_capacity"),
                "vehicle_gross_weight": data.get("vehicle_gross_weight"),
                "no_cylinders": data.get("no_cylinders"),
                "seat_capacity": data.get("seat_capacity"),
                "sleeper_capacity": data.get("sleeper_capacity"),
                "standing_capacity": data.get("standing_capacity"),
                "wheelbase": data.get("wheelbase"),
                "unladen_weight": data.get("unladen_weight"),
                "vehicle_category_description": data.get("vehicle_category_description"),
                "pucc_number": data.get("pucc_number"),
                "pucc_upto": data.get("pucc_upto"),
                "permit_number": data.get("permit_number"),
                "permit_issue_date": data.get("permit_issue_date"),
                "permit_valid_from": data.get("permit_valid_from"),
                "permit_valid_upto": data.get("permit_valid_upto"),
                "permit_type": data.get("permit_type"),
                "national_permit_number": data.get("national_permit_number"),
                "national_permit_upto": data.get("national_permit_upto"),
                "national_permit_issued_by": data.get("national_permit_issued_by"),
                "non_use_status": data.get("non_use_status"),
                "non_use_from": data.get("non_use_from"),
                "non_use_to": data.get("non_use_to"),
                "blacklist_status": data.get("blacklist_status"),
                "noc_details": data.get("noc_details"),
                "owner_number": data.get("owner_number"),
                "rc_status": data.get("rc_status"),
                "masked_name": data.get("masked_name"),
                "challan_details": data.get("challan_details"),
                "variant": data.get("variant"),
            }

            serializer = VehicleRCVerificationResponseSerializer(data=response_payload)
            serializer.is_valid(raise_exception=True)
            return serializer.data
        except Exception as e:
            error_response = {
                "success": False,
                "message": f"Verification failed: {str(e)}",
                "provider": "deepvue"
            }
            serializer = VehicleRCVerificationResponseSerializer(data=error_response)
            serializer.is_valid()
            return serializer.data
