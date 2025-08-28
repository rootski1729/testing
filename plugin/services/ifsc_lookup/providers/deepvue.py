import httpx
from typing import TYPE_CHECKING
from .abc import AbstractIFSCVerificationProvider
from plugin.utils.deepvue_auth import DeepvueAuth
from ..serializers import (
    IFSCVerificationRequestSerializer,
    IFSCVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractIFSCVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.auth = DeepvueAuth(client_id, client_secret)

    def verify_ifsc(
        self, plugin: "Plugin", request: IFSCVerificationRequestSerializer
    ) -> IFSCVerificationResponseSerializer:
        try:
            ifsc = request.validated_data["ifsc"]

            result = self.auth.make_request(
                "GET",
                "/v1/verification/ifsc",
                params={"ifsc": ifsc},
            )
            
            data = result.get("data", {}) or {}
            
            response_payload = {
                "message": result.get("message"),
                "code": result.get("code"),
                "sub_code": result.get("sub_code"),
                "transaction_id": result.get("transaction_id"),
                "MICR": data.get("MICR"),
                "BRANCH": data.get("BRANCH"),
                "ADDRESS": data.get("ADDRESS"),
                "STATE": data.get("STATE"),
                "CONTACT": data.get("CONTACT"),
                "UPI": data.get("UPI"),
                "RTGS": data.get("RTGS"),
                "CITY": data.get("CITY"),
                "CENTRE": data.get("CENTRE"),
                "DISTRICT": data.get("DISTRICT"),
                "NEFT": data.get("NEFT"),
                "IMPS": data.get("IMPS"),
                "SWIFT": data.get("SWIFT"),
                "ISO3166": data.get("ISO3166"),
                "BANK": data.get("BANK"),
                "BANKCODE": data.get("BANKCODE"),
                "IFSC": data.get("IFSC"),
            }

            serializer = IFSCVerificationResponseSerializer(data=response_payload)
            serializer.is_valid(raise_exception=True)
            return serializer.data
        
        except httpx.HTTPError as e:
            # Handle HTTP errors
            return IFSCVerificationResponseSerializer(
                data={
                    "message": str(e),
                    "code": 400
                    }
            )
        except Exception as e:
            return IFSCVerificationResponseSerializer(
                data={
                    "message": str(e),
                    "code": 500
                }
            )