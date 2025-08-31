from typing import TYPE_CHECKING

from .abc import AbstractPANValidationProvider

if TYPE_CHECKING:
    from plugin.models import Plugin


class NSDL(AbstractPANValidationProvider):

    async def validate_pan(self, plugin: "Plugin", pan_number: str) -> bool:
        # Implement NSDL-specific PAN validation logic here
        pass
