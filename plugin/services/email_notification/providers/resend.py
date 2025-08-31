import resend
from typing import TYPE_CHECKING
from ..models import EmailRequest, EmailResponse
from .abc import AbstractEmailProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class RESEND(AbstractEmailProvider):
    def __init__(self, plugin: "Plugin"):
        super().__init__(plugin)
        # API Key will be stored in Plugin model (plugin.api_key)
        resend.api_key = plugin.api_key

    def run(self, plugin: "Plugin", request: EmailRequest) -> EmailResponse:
        try:
            params = {
                "from": request.from_email,
                "to": request.to,
                "subject": request.subject,
                "html": request.html,
            }

            email = resend.Emails.send(params)

            return EmailResponse(
                success=True,
                message="Email sent successfully",
                id=email.get("id") if isinstance(email, dict) else str(email),
            )

        except Exception as e:
            return EmailResponse(
                success=False,
                message=f"Resend email failed: {str(e)}",
                id=None,
            )
