from typing import TYPE_CHECKING
import httpx
from ..models import PANVerificationRequest, PANVerificationResponse
from .abc import AbstractPANValidationProvider
from plugin.utils.deepvue_auth import DeepvueAuth

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractPANValidationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        self.auth = DeepvueAuth(plugin.client_id, plugin.client_secret)

    def validate_pan(
        self, plugin: "Plugin", request: PANVerificationRequest
    ) -> PANVerificationResponse:
        try:
            # Extract pan_number directly from Pydantic model
            pan_number = request.pan_number

            result = self.auth.make_request(
                "GET",
                "/v2/verification/pan-plus",
                params={"pan_number": pan_number},
            )

            data = result.get("data", {}) or {}

            return PANVerificationResponse(
                success=(result.get("sub_code") == "SUCCESS"),
                message=result.get("message"),
                request_id=result.get("transaction_id"),
                transaction_id=result.get("transaction_id"),
                sub_code=result.get("sub_code"),

                pan_number=data.get("pan_number"),
                full_name=data.get("full_name"),
                full_name_split=data.get("full_name_split"),
                category=data.get("category"),
                gender=data.get("gender"),
                dob=data.get("dob"),
                masked_aadhaar=data.get("masked_aadhaar"),
                aadhaar_linked=data.get("aadhaar_linked"),
            )

        except Exception as e:
            return PANVerificationResponse(success=False, message=f"PAN validation failed: {str(e)}")
