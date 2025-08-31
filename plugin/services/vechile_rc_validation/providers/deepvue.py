from typing import TYPE_CHECKING

import httpx

from plugin.utils.cache_decorator import auto_cached_provider_method
from plugin.utils.deepvue_auth import DeepvueAuth

from ..models import VehicleRCVerificationRequest, VehicleRCVerificationResponse
from .abc import AbstractVehicleRCVerificationProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractVehicleRCVerificationProvider):

    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        self.auth = DeepvueAuth(plugin.client_id, plugin.client_secret)

    @auto_cached_provider_method()
    def run(
        self, plugin: "Plugin", request: VehicleRCVerificationRequest
    ) -> VehicleRCVerificationResponse:
        try:
            result = self.auth.make_request(
                "GET",
                "/v1/verification/rc-advanced",
                params={"rc_number": request.rc_number},
            )

            data = result.get("data", {}) or {}

            response_payload = {
                "success": (result.get("sub_code") == "SUCCESS"),
                "message": result.get("message"),
                "transaction_id": result.get("transaction_id"),
                "sub_code": result.get("sub_code"),
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
                "model": data.get("maker_model"),
                "body_type": data.get("body_type"),
                "vehicle_fuel_type": data.get("fuel_type"),
                "vehicle_color": data.get("color"),
                "norms_type": data.get("norms_type"),
                "fit_up_to": data.get("fit_up_to"),
                "financer": data.get("financer"),
                "insurance_company": data.get("insurance_company"),
                "last_policy_number": data.get("insurance_policy_number"),
                "insurance_upto": data.get("insurance_upto"),
                "manufactured_month_year": data.get("manufacturing_date"),
                "registered_at": data.get("registered_at"),
                "latest_by": data.get("latest_by"),
                "less_info": data.get("less_info"),
                "noc_details": data.get("noc_details"),
                "rc_status": data.get("rc_status"),
            }

            return VehicleRCVerificationResponse(**response_payload)

        except Exception as e:
            return VehicleRCVerificationResponse(
                success=False,
                message=f"Verification failed: {str(e)}",
            )
