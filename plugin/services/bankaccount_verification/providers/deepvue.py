import httpx
from typing import TYPE_CHECKING
from .abc import AbstractBankAccountVerificationProvider
from plugin.utils.deepvue_auth import DeepvueAuth
from ..serializers import (
    BankAccountVerificationRequestSerializer,
    BankAccountVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class DEEPVUE(AbstractBankAccountVerificationProvider):
    BASE_URL = "https://production.deepvue.tech"

    def __init__(self, client_id: str, client_secret: str):
        self.auth = DeepvueAuth(client_id, client_secret)

    def verify_bank_account(
        self, plugin: "Plugin", request: BankAccountVerificationRequestSerializer
    ) -> BankAccountVerificationResponseSerializer:
        try:
            account_number = request.validated_data["account_number"]
            ifsc = request.validated_data["ifsc"]
            name = request.validated_data["name"]

            response = self.auth.make_request(
                "GET",
                "/v1/verification/bankaccount",
                params={
                    "account_number": account_number,
                    "ifsc": ifsc,
                    "name": name,
                },
            )

            # Normalize Deepvue response
            response_payload = {
                "success": True if response.get("code") == 200 else False,
                "message": response.get("data", {}).get("message", "Verification completed"),
                "provider": "deepvue",
                "code": response.get("code"),
                "timestamp": response.get("timestamp"),
                "transaction_id": response.get("transaction_id"),
                "account_exists": response.get("data", {}).get("account_exists"),
                "name_at_bank": response.get("data", {}).get("name_at_bank"),
                "utr": response.get("data", {}).get("utr"),
                "amount_deposited": response.get("data", {}).get("amount_deposited"),
                "name_information": response.get("data", {}).get("name_information"),
            }

            serializer = BankAccountVerificationResponseSerializer(data=response_payload)
            serializer.is_valid(raise_exception=True)
            return serializer.data

        except Exception as e:
            error_response = {
                "success": False,
                "message": f"Bank verification failed: {str(e)}",
                "provider": "deepvue",
            }
            serializer = BankAccountVerificationResponseSerializer(data=error_response)
            serializer.is_valid(raise_exception=True)
            return serializer.data
