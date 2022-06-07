import abc
import typing


class BaseDeploy(abc.ABC):

    def __init__(self, use_terraform: typing.Optional[bool] = False) -> None:
        super().__init__()
        self._use_terraform = use_terraform

    @abc.abstractmethod
    def write_scripts(self) -> None:
        pass

