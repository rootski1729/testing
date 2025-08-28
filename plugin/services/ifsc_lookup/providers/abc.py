from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..serializers import (
    IFSCVerificationRequestSerializer,
    IFSCVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractIFSCVerificationProvider(ABC):
    @abstractmethod
    def verify_ifsc(
        self, plugin: "Plugin", request: IFSCVerificationRequestSerializer
    ) -> IFSCVerificationResponseSerializer:
        pass
