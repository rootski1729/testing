import httpx
from typing import TYPE_CHECKING
from .abc import AbstractDrivingLicenseVerificationProvider
from plugin.utils.deepvue_auth import DeepvueAuth
from ..serializers import (
    DrivingLicenseVerificationRequestSerializer,
    DrivingLicenseVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractDrivingLicenseVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.auth = DeepvueAuth(client_id, client_secret)

    def verify_driving_license(
        self, plugin: "Plugin", request: DrivingLicenseVerificationRequestSerializer
    ) -> DrivingLicenseVerificationResponseSerializer:
        try:
            dl_number = request.validated_data["dl_number"]
            dob = request.validated_data["dob"]

            post_result = self.auth.make_request(
                "POST",
                "/v1/verification/post-driving-license",
                params={"dl_number": dl_number, "dob": str(dob)},
            )
            
            
            request_id = post_result.get("request_id")
            if not request_id:
                return {"success": False, "message": "No request_id returned", "provider": "deepvue"}

            get_result = self.auth.make_request(
                "GET",
                "/v1/verification/get-driving-license",
                params={"request_id": request_id},
            )
            

            if not isinstance(get_result, list) or not get_result:
                return {"success": False, "message": "Invalid response format", "provider": "deepvue"}

            result_data = get_result[0].get("result", {}).get("source_output", {})

            response_payload = {
                "success": True,
                "message": "Driving license verified successfully",
                "provider": "deepvue",
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

            serializer = DrivingLicenseVerificationResponseSerializer(data=response_payload)
            serializer.is_valid(raise_exception=True)
            return serializer.data

        except Exception as e:
            error_response = {"success": False, "message": f"Verification failed: {str(e)}", "provider": "deepvue"}
            serializer = DrivingLicenseVerificationResponseSerializer(data=error_response)
            serializer.is_valid()
            return serializer.data
