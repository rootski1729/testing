from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..serializers import (
    BankAccountVerificationRequestSerializer,
    BankAccountVerificationResponseSerializer,
)

if TYPE_CHECKING:
    from plugin.models import Plugin


class AbstractBankAccountVerificationProvider(ABC):
    @abstractmethod
    def verify_bank_account(
        self, plugin: "Plugin", request: BankAccountVerificationRequestSerializer
    ) -> BankAccountVerificationResponseSerializer:
        pass
