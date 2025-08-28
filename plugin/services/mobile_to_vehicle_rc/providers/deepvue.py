import httpx
from typing import TYPE_CHECKING
from .abc import AbstractMobileToVehicleRCProvider
from plugin.utils.deepvue_auth import DeepvueAuth
from ..serializers import (
    MobileToVehicleRCRequestSerializer,
    MobileToVehicleRCResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractMobileToVehicleRCProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.auth = DeepvueAuth(client_id, client_secret)

    def fetch_vehicle_rc(
        self, plugin: "Plugin", request: MobileToVehicleRCRequestSerializer
    ) -> MobileToVehicleRCResponseSerializer:
        try:
            mobile_number = request.validated_data["mobile_number"]

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

            serializer = MobileToVehicleRCResponseSerializer(data=response_payload)
            serializer.is_valid(raise_exception=True)
            return serializer.data

        except Exception as e:
            error_response = {
                "success": False,
                "message": f"Mobile-to-RC fetch failed: {str(e)}",
                "provider": "deepvue",
            }
            serializer = MobileToVehicleRCResponseSerializer(data=error_response)
            serializer.is_valid()
            return serializer.data
