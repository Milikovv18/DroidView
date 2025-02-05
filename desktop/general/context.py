from networking.content_supplier import SupplierData
from . import AdbController


class Context:
    screen_res : tuple[int, int]

    _state = None

    def __init__(self, device_controller : AdbController) -> None:
        # Import here due to circular dependency with State
        from .states import InitialState
        self.setState(InitialState())
        self.device_controller = device_controller

    def setState(self, state):
        print(f"Context: Transitioning to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def handle_device(self, device_name : str):
        self._state.handle_device(device_name)

    def is_app_installed(self) -> bool:
        return self._state.is_app_installed()

    def install_app(self):
        self._state.install_app()

    def start_stream(self):
        self._state.start_stream()

    def capture(self):
        self._state.capture()

    def get_data(self) -> SupplierData:
        return self._state.get_data()

    def disconnect(self):
        self._state.disconnect()
