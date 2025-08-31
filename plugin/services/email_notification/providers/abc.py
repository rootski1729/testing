from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..models import EmailRequest, EmailResponse

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractEmailProvider(ABC):
    def __init__(self, plugin: "Plugin"):
        self.plugin = plugin

    @abstractmethod
    def run(self, plugin: "Plugin", request: EmailRequest) -> EmailResponse:
        pass
