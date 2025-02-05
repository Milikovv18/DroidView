from .state import State
from .ready import ReadyState

class AppNotInstalledState(State):
    def is_app_installed(self) -> bool:
        return False

    def install_app(self):
        self.context.device_controller.install_app()

        self.context.setState(ReadyState())
