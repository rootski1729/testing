from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..models import IFSCVerificationRequest, IFSCVerificationResponse

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractIFSCVerificationProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin

    @abstractmethod
    def verify_ifsc(
        self, plugin: "Plugin", request: IFSCVerificationRequest
    ) -> IFSCVerificationResponse:
        pass
