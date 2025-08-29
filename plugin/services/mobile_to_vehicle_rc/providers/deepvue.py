import httpx
from typing import TYPE_CHECKING
from .abc import AbstractMobileToVehicleRCProvider
from plugin.utils.deepvue_auth import DeepvueAuth
from ..models import (
    MobileToVehicleRCRequest,
    MobileToVehicleRCResponse,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractMobileToVehicleRCProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        self.auth = DeepvueAuth(plugin.client_id, plugin.client_secret)

    def fetch_vehicle_rc(
        self, plugin: "Plugin", request: MobileToVehicleRCRequest
    ) -> MobileToVehicleRCResponse:
        try:
            mobile_number = request.mobile_number

            response_data = self.auth.make_request(
                "GET",
                "/v1/mobile-intelligence/mobile-to-vehicle-rc",
                params={"mobile_number": mobile_number},
            )

            response_payload = {
                "success": response_data.get("code") == 200,
                "message": response_data.get("message", ""),
                "provider": "deepvue",
                "code": response_data.get("code"),
                "timestamp": response_data.get("timestamp"),
                "transaction_id": response_data.get("transaction_id"),
                "sub_code": response_data.get("sub_code"),
                "data": response_data.get("data"),
            }

            return MobileToVehicleRCResponse(**response_payload)

        except Exception as e:
            return MobileToVehicleRCResponse(
                success=False,
                message=f"Mobile-to-RC fetch failed: {str(e)}",
                provider="deepvue",
            )
