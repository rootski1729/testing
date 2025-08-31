from typing import TYPE_CHECKING

import httpx

from plugin.utils.deepvue_auth import DeepvueAuth

from ..models import IFSCVerificationRequest, IFSCVerificationResponse
from .abc import AbstractIFSCVerificationProvider

if TYPE_CHECKING:
    from plugin.models import Plugin

from plugin.utils.cache_decorator import auto_cached_provider_method


class DEEPVUE(AbstractIFSCVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        super().__init__(plugin)
        self.auth = DeepvueAuth(plugin.client_id, plugin.client_secret)

    @auto_cached_provider_method()
    def run(
        self, plugin: "Plugin", request: IFSCVerificationRequest
    ) -> IFSCVerificationResponse:
        try:
            result = self.auth.make_request(
                "GET",
                "/v1/verification/ifsc",
                params={"ifsc": request.ifsc},
            )

            data = result.get("data", {}) or {}

            return IFSCVerificationResponse(
                message=result.get("message"),
                code=result.get("code"),
                sub_code=result.get("sub_code"),
                transaction_id=result.get("transaction_id"),
                MICR=data.get("MICR"),
                BRANCH=data.get("BRANCH"),
                ADDRESS=data.get("ADDRESS"),
                STATE=data.get("STATE"),
                CONTACT=data.get("CONTACT"),
                UPI=data.get("UPI"),
                RTGS=data.get("RTGS"),
                CITY=data.get("CITY"),
                CENTRE=data.get("CENTRE"),
                DISTRICT=data.get("DISTRICT"),
                NEFT=data.get("NEFT"),
                IMPS=data.get("IMPS"),
                SWIFT=data.get("SWIFT"),
                ISO3166=data.get("ISO3166"),
                BANK=data.get("BANK"),
                BANKCODE=data.get("BANKCODE"),
                IFSC=data.get("IFSC"),
            )

        except httpx.HTTPError as e:
            return IFSCVerificationResponse(message=str(e), code=400)

        except Exception as e:
            return IFSCVerificationResponse(message=str(e), code=500)
