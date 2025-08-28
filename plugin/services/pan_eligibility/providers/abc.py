from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plugin.models import Plugin

class AbstractPANEligibilityProvider(ABC):

    @abstractmethod
    async def is_pan_eligible(self, plugin: "Plugin", pan_number: str) -> bool:
        pass
