from abc import ABC

from ..context import Context


class State(ABC):
    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context : Context) -> None:
        self._context = context

    
    def handle_device(self, device_name : str):
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)
    
    def is_app_installed(self) -> bool:
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)
    
    def install_app(self):
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)
    
    def start_stream(self):
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)
    
    def capture(self):
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)
    
    def get_data(self):
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)

    def disconnect(self):
        raise NotImplementedError("Method is not available in " + self.__class__.__name__)
