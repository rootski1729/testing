from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..models import PANEligibilityRequest, PANEligibilityResponse

if TYPE_CHECKING:
    from plugin.models import Plugin
class AbstractPANEligibilityProvider(ABC):
    def __init__(self,plugin: "Plugin"):
        self.plugin = plugin
    
    @abstractmethod
    def run(self, request: PANEligibilityRequest) -> PANEligibilityResponse:
        pass
