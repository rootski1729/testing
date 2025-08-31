import httpx
from typing import TYPE_CHECKING
from ..models import PANEligibilityRequest, PANEligibilityResponse
from .abc import AbstractPANEligibilityProvider

from plugin.utils.cache_decorator import auto_cached_provider_method

if TYPE_CHECKING:
    from plugin.models import Plugin


class UNISEN(AbstractPANEligibilityProvider):
    BASE_URL = "https://unisen.app/verification/api/itrex/pan/verify/"

    def __init__(self, plugin: "Plugin"):
        super().__init__(plugin)
        self.api_key = plugin.api_key

    @auto_cached_provider_method()
    def run(self, plugin: "Plugin", request: PANEligibilityRequest) -> PANEligibilityResponse:
        payload = request.model_dump()

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    self.BASE_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Token {self.api_key}",
                    },
                    json=payload,
                )
        except httpx.RequestError as e:
            return PANEligibilityResponse(
                success=False,
                verification_status="FAILED",
                message=f"Network error: {str(e)}",
                error_code="NETWORK_ERROR",
            )

        try:
            data = resp.json()
        except ValueError:
            return PANEligibilityResponse(
                success=False,
                verification_status="FAILED",
                message=f"Invalid response: {resp.text}",
                error_code="INVALID_RESPONSE",
            )

        if resp.status_code == 200 and "result" in data:
            result = data["result"]
            return PANEligibilityResponse(
                success=True,
                verification_status=result.get("verification_status"),
                message=result.get("message"),
                verified_at=result.get("verified_at"),
                agent_enum=result.get("agent_enum"),
                is_cached_response=data.get("is_cached_response"),
            )

        if resp.status_code == 402:
            return PANEligibilityResponse(
                success=False,
                verification_status="FAILED",
                error_code="INSUFFICIENT_BALANCE",
                message="Insufficient balance. Please add funds to your account.",
            )

        return PANEligibilityResponse(
            success=False,
            verification_status="FAILED",
            error_code=data.get("error_code"),
            message=data.get("error"),
        )
