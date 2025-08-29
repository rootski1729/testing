import httpx
from typing import TYPE_CHECKING
from .abc import AbstractSMSProvider
from ..models import SMSRequest, SMSResponse

if TYPE_CHECKING:
    from plugin.models import Plugin


class Cell(AbstractSMSProvider):
    BASE_URL = "https://sms1.cell24x7.com/httpReceiver/api/sendText"

    def __init__(self, plugin: "Plugin"):
        super().__init__(plugin)

    def send_sms(self, plugin: "Plugin", request: SMSRequest) -> SMSResponse:
        try:
            payload = {
                "apiK": plugin.api_key,  # Inject from DB
                **request.model_dump(),
            }

            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    self.BASE_URL,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
                data = resp.json()

            return SMSResponse(
                success=(resp.status_code == 200 and "response_id" in data),
                message=data.get("message", "SMS Sent Successfully"),
                code=resp.status_code,
                response_id=data.get("response_id"),
            )

        except Exception as e:
            return SMSResponse(
                success=False,
                message=f"SMS sending failed: {str(e)}",
                code=500,
            )
