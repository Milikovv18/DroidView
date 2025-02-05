from abc import ABC

from ..context import Context
from .state import State
from .terminal import TerminalState
from networking import *


rtmp_supplier = RtmpSupplier()


class ActiveState(State, ABC):
    supplier : ContentSupplier


class StreamingState(ActiveState):
    @property
    def context(self) -> Context:
        return self._context
    
    @context.setter
    def context(self, context) -> None:
        self._context = context
        self.supplier = rtmp_supplier
        self.supplier.set_resolution(self.context.screen_res)

    def is_app_installed(self) -> bool:
        return True

    def capture(self):
        self.context.device_controller.request_transmission("ACCESSIBILITY_DRIVEN")
        self.context.setState(CapturingState())

    def get_data(self) -> SupplierData:
        return self.supplier.get_data()

    def disconnect(self):
        # Stop RTMP server
        self.context.setState(TerminalState())


class CapturingState(ActiveState):
    @property
    def context(self) -> Context:
        return self._context
    
    @context.setter
    def context(self, context) -> None:
        self._context = context
        self.supplier = rtmp_supplier
        self.supplier.set_resolution(self.context.screen_res)

    def is_app_installed(self) -> bool:
        return True
    
    def start_stream(self):
        self.context.device_controller.request_transmission("VIDEO_DRIVEN")
        self.context.setState(StreamingState())

    def get_data(self) -> SupplierData:
        # Getting data only was, then suspending
        data = self.supplier.get_data()

        if data.nodes is not None and "booleans" in data.nodes:
            self.context.device_controller.request_transmission("STUB")
            self.context.setState(SuspendedState())

        return data

    def disconnect(self):
        # Stop TCP server
        self.context.setState(TerminalState())


class SuspendedState(ActiveState):
    @property
    def context(self) -> Context:
        return self._context
    
    @context.setter
    def context(self, context) -> None:
        self._context = context
        self.supplier = rtmp_supplier
        self.supplier.set_resolution(self.context.screen_res)

    def is_app_installed(self) -> bool:
        return True
    
    def start_stream(self):
        self.context.device_controller.request_transmission("VIDEO_DRIVEN")
        self.context.setState(StreamingState())

    def capture(self):
        self.context.device_controller.request_transmission("ACCESSIBILITY_DRIVEN")
        self.context.setState(CapturingState())

    def get_data(self):
        raise SupplierClosedException()
