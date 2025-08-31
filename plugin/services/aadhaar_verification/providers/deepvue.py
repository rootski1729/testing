from typing import TYPE_CHECKING, Any, Dict

import httpx

from plugin.utils.cache_decorator import auto_cached_provider_method

from ..models import (
    AadhaarOTPGenerateRequest,
    AadhaarOTPGenerateResponse,
    AadhaarOTPVerifyRequest,
    AadhaarVerificationResponse,
)
from .abc import AbstractAadhaarVerificationProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractAadhaarVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        self.client_id = plugin.client_id
        self.client_secret = plugin.client_secret

    def _make_request(
        self, method: str, endpoint: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Helper for making requests to Deepvue API
        Deepvue requires query params (not JSON body).
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "x-api-key": self.client_secret,
            "client-id": self.client_id,
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=30) as client:
                response = client.request(method, url, params=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "message": f"HTTP {e.response.status_code}: {e.response.text}",
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def generate_otp(
        self, plugin: "Plugin", request: AadhaarOTPGenerateRequest
    ) -> AadhaarOTPGenerateResponse:
        try:
            payload = request.dict()
            result = self._make_request(
                "POST", "/v2/ekyc/aadhaar/generate-otp", payload
            )

            return AadhaarOTPGenerateResponse(
                success=(result.get("sub_code") == "SUCCESS"),
                message=result.get("message", ""),
                code=result.get("code"),
                reference_id=result.get("reference_id"),
                transaction_id=result.get("transaction_id"),
                sub_code=result.get("sub_code"),
            )
        except Exception as e:
            return AadhaarOTPGenerateResponse(success=False, message=str(e))

    @auto_cached_provider_method(exclude_fields=["otp", "reference_id"])
    def verify_otp(
        self, plugin: "Plugin", request: AadhaarOTPVerifyRequest
    ) -> AadhaarVerificationResponse:
        try:
            payload = request.dict()
            result = self._make_request("POST", "/v2/ekyc/aadhaar/verify-otp", payload)
            data = result.get("data", {}) or {}

            return AadhaarVerificationResponse(
                success=(result.get("sub_code") == "SUCCESS"),
                message=result.get("message", ""),
                code=result.get("code"),
                aadhaar_number=data.get("aadhaar_number"),
                masked_number=data.get("maskedNumber"),
                name=data.get("name"),
                date_of_birth=data.get("dateOfBirth"),
                gender=data.get("gender"),
                email=data.get("email"),
                phone=data.get("phone"),
                address=data.get("address"),
                photo=data.get("photo"),
                document_pdf=data.get("document_pdf"),
                aadhaar_linked_mobile_match=data.get("aadhaar_linked_mobile_match"),
                transaction_id=result.get("transaction_id"),
                sub_code=result.get("sub_code"),
            )
        except Exception as e:
            return AadhaarVerificationResponse(success=False, message=str(e))
