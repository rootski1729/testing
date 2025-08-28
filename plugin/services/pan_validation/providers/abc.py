from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..serializers import PANVerificationRequestSerializer, PANVerificationResponseSerializer

if TYPE_CHECKING:
    from plugin.models import Plugin

class AbstractPANValidationProvider(ABC):

    @abstractmethod
    def validate_pan(self, plugin: "Plugin", request: PANVerificationRequestSerializer) -> PANVerificationResponseSerializer:
        pass
