from typing import TYPE_CHECKING

from plugin.utils.cache_decorator import auto_cached_provider_method
from plugin.utils.deepvue_auth import DeepvueAuth

from ..models import BankAccountVerificationRequest, BankAccountVerificationResponse
from .abc import AbstractBankAccountVerificationProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractBankAccountVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, plugin: "Plugin"):
        self.auth = DeepvueAuth(plugin.client_id, plugin.client_secret)

    @auto_cached_provider_method()
    def run(
        self, plugin: "Plugin", request: BankAccountVerificationRequest
    ) -> BankAccountVerificationResponse:
        try:
            response = self.auth.make_request(
                "GET",
                "/v1/verification/bankaccount",
                params=request.model_dump(),
            )
            response_payload = {
                "success": True if response.get("code") == 200 else False,
                "message": response.get("data", {}).get(
                    "message", "Verification completed"
                ),
                "code": response.get("code"),
                "timestamp": response.get("timestamp"),
                "transaction_id": response.get("transaction_id"),
                "account_exists": response.get("data", {}).get("account_exists"),
                "name_at_bank": response.get("data", {}).get("name_at_bank"),
                "utr": response.get("data", {}).get("utr"),
                "amount_deposited": response.get("data", {}).get("amount_deposited"),
                "name_information": response.get("data", {}).get("name_information"),
            }

            return BankAccountVerificationResponse(**response_payload)

        except Exception as e:
            error_response = {
                "success": False,
                "message": f"Bank verification failed: {str(e)}",
                "provider": "deepvue",
            }
            return BankAccountVerificationResponse(**error_response)
