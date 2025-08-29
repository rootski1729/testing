from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..models import SMSRequest, SMSResponse

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractSMSProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin

    @abstractmethod
    def send_sms(self, plugin: "Plugin", request: SMSRequest) -> SMSResponse:
        pass
