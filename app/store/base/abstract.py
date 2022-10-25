from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from web.app import Application


class AbstractAccessor(ABC):

    @abstractmethod
    async def connect(self, app: "Application"):
        ...

    async def disconnect(self, app: "Application"):
        ...
