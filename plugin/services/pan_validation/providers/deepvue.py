from typing import TYPE_CHECKING
import httpx
from .abc import AbstractPANValidationProvider
from ..serializers import PANVerificationRequestSerializer, PANVerificationResponseSerializer
from plugin.utils.deepvue_auth import DeepvueAuth

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractPANValidationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.auth = DeepvueAuth(client_id, client_secret)

    def validate_pan(
        self, plugin: "Plugin", request: PANVerificationRequestSerializer
    ) -> PANVerificationResponseSerializer:
        
        try:
    
            pan_number = request.validated_data["pan_number"]

            
            result = self.auth.make_request(
                "GET",
                "/v2/verification/pan-plus",
                params={"pan_number": pan_number},
            )

            data = result.get("data", {}) or {}

            response_data = {
                "success": (result.get("sub_code") == "SUCCESS"),
                "message": result.get("message"),
                "provider": "deepvue",
                "request_id": result.get("transaction_id"),
                "transaction_id": result.get("transaction_id"),
                "sub_code": result.get("sub_code"),

                "pan_number": data.get("pan_number"),
                "full_name": data.get("full_name"),
                "full_name_split": data.get("full_name_split"),
                "category": data.get("category"),
                "gender": data.get("gender"),
                "dob": data.get("dob"),
                "masked_aadhaar": data.get("masked_aadhaar"),
                "aadhaar_linked": data.get("aadhaar_linked"),
            }

            serializer = PANVerificationResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return serializer.data
        except Exception as e:
            return PANVerificationResponseSerializer(data={"success": False, "message": str(e)})
