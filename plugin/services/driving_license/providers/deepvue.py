from typing import TYPE_CHECKING

import httpx

from plugin.utils.cache_decorator import auto_cached_provider_method
from plugin.utils.deepvue_auth import DeepvueAuth

from ..models import (
    DrivingLicenseVerificationRequest,
    DrivingLicenseVerificationResponse,
)
from .abc import AbstractDrivingLicenseVerificationProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractDrivingLicenseVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        self.auth = DeepvueAuth(plugin.client_id, plugin.client_secret)

    @auto_cached_provider_method(exclude_fields=["dob"])
    def run(
        self, plugin: "Plugin", request: DrivingLicenseVerificationRequest
    ) -> DrivingLicenseVerificationResponse:
        try:
            post_result = self.auth.make_request(
                "POST",
                "/v1/verification/post-driving-license",
                params=request.model_dump(),
            )

            request_id = post_result.get("request_id")
            if not request_id:
                return DrivingLicenseVerificationResponse(
                    success=False,
                    message="No request_id returned",
                    provider="deepvue",
                )

            # Step 2: Fetch result
            get_result = self.auth.make_request(
                "GET",
                "/v1/verification/get-driving-license",
                params={"request_id": request_id},
            )

            if not isinstance(get_result, list) or not get_result:
                return DrivingLicenseVerificationResponse(
                    success=False,
                    message="Invalid response format",
                    provider="deepvue",
                )

            result_data = get_result[0].get("result", {}).get("source_output", {})

            response_payload = {
                "success": True,
                "message": "Driving license verified successfully",
                "request_id": request_id,
                "id_number": result_data.get("id_number"),
                "name": result_data.get("name"),
                "dob": result_data.get("dob"),
                "relatives_name": result_data.get("relatives_name"),
                "address": result_data.get("address"),
                "issuing_rto_name": result_data.get("issuing_rto_name"),
                "date_of_issue": result_data.get("date_of_issue"),
                "dl_status": result_data.get("dl_status"),
                "nt_validity_from": result_data.get("nt_validity_from"),
                "nt_validity_to": result_data.get("nt_validity_to"),
                "t_validity_from": result_data.get("t_validity_from"),
                "t_validity_to": result_data.get("t_validity_to"),
                "cov_details": result_data.get("cov_details"),
            }

            return DrivingLicenseVerificationResponse(**response_payload)

        except Exception as e:
            return DrivingLicenseVerificationResponse(
                success=False,
                message=f"Driving license verification failed: {str(e)}",
                provider="deepvue",
            )
