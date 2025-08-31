from typing import TYPE_CHECKING

import httpx

from ..models import SMSRequest, SMSResponse
from .abc import AbstractSMSProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class Cell(AbstractSMSProvider):
    BASE_URL = "https://sms1.cell24x7.com/httpReceiver/api/sendText"

    def __init__(self, plugin: "Plugin"):
        super().__init__(plugin)

    def run(self, plugin: "Plugin", request: SMSRequest) -> SMSResponse:
        payload = {
            "apiK": plugin.api_key,
            **request.model_dump(),
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    self.BASE_URL,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as e:
            return SMSResponse(
                success=False,
                message=f"Network error: {str(e)}",
                code=None,
                response_id=None,
            )

        # Try parsing JSON, fallback to text
        try:
            data = resp.json()
        except ValueError:
            data = {"raw_response": resp.text.strip()}

        # Determine success
        is_success = resp.status_code == 200 and (
            "response_id" in data or "raw_response" in data
        )

        return SMSResponse(
            success=is_success,
            message=data.get("message")
            or data.get("raw_response")
            or f"HTTP {resp.status_code}",
            code=resp.status_code,
        )
