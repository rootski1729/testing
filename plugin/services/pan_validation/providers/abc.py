from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..models import PANVerificationRequest, PANVerificationResponse

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractPANValidationProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin

    @abstractmethod
    def validate_pan(
        self, plugin: "Plugin", request: PANVerificationRequest
    ) -> PANVerificationResponse:
        pass
