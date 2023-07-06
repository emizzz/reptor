import typing
from abc import abstractmethod

from .conf import ConfigProtocol
from reptor.core.logger import ReptorAdapter
from reptor.core.console import Console


class ReptorProtocol(typing.Protocol):
    logger: ReptorAdapter
    console: Console

    @abstractmethod
    def get_config(self) -> ConfigProtocol:
        ...
