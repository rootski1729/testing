import httpx
from typing import TYPE_CHECKING, Dict, Any
from .abc import AbstractAadhaarVerificationProvider
from ..serializers import (
    AadhaarOTPGenerateRequestSerializer,
    AadhaarOTPGenerateResponseSerializer,
    AadhaarOTPVerifyRequestSerializer,
    AadhaarVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractAadhaarVerificationProvider):

    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "x-api-key": self.client_secret,
            "client-id": self.client_id,
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=30) as client:
                response = client.request(method, url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"success": False, "message": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def generate_otp(self, plugin: "Plugin", request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request_serializer = AadhaarOTPGenerateRequestSerializer(data=request_data)
            request_serializer.is_valid(raise_exception=True)
            validated = request_serializer.validated_data

            params = {
                "aadhaar_number": validated["aadhaar_number"],
                "consent": validated.get("consent", "Y"),
                "purpose": validated.get("purpose", "ForKYC"),
            }

            result = self._make_request("POST", "/v2/ekyc/aadhaar/generate-otp", params)

            response_serializer = AadhaarOTPGenerateResponseSerializer(data={
                "success": result.get("success", True),
                "message": result.get("message", ""),
                "reference_id": result.get("reference_id"),
                "transaction_id": result.get("transaction_id"),
                "sub_code": result.get("sub_code"),
            })
            response_serializer.is_valid(raise_exception=True)
            return response_serializer.data
        
        except Exception as e:
            response_serializer = AadhaarOTPGenerateResponseSerializer(data={
                "success": False,
                "message": str(e),
            })
            response_serializer.is_valid(raise_exception=True)
            return response_serializer.data

    def verify_otp(self, plugin: "Plugin", request_data: Dict[str, Any]) -> Dict[str, Any]:
        request_serializer = AadhaarOTPVerifyRequestSerializer(data=request_data)
        request_serializer.is_valid(raise_exception=True)
        validated = request_serializer.validated_data

        params = {
            "otp": validated["otp"],
            "reference_id": validated["reference_id"],
            "consent": validated.get("consent", "Y"),
            "purpose": "ForKYC",
            "mobile_number": validated["mobile_number"],
            "generate_pdf": str(validated.get("generate_pdf", False)).lower(),
        }

        result = self._make_request("POST", "/v2/ekyc/aadhaar/verify-otp", params)

        data = result.get("data", {}) or {}
        response_serializer = AadhaarVerificationResponseSerializer(data={
            "success": result.get("success", True),
            "message": result.get("message", ""),
            "aadhaar_number": data.get("aadhaar_number"),
            "masked_number": data.get("maskedNumber"),
            "name": data.get("name"),
            "date_of_birth": data.get("dateOfBirth"),
            "gender": data.get("gender"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "photo": data.get("photo"),
            "document_pdf": data.get("document_pdf"),
            "aadhaar_linked_mobile_match": data.get("aadhaar_linked_mobile_match"),
            "transaction_id": result.get("transaction_id"),
            "sub_code": result.get("sub_code"),
        })
        response_serializer.is_valid(raise_exception=True)
        return response_serializer.data
