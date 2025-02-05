from .state import State
from .ready import ReadyState
from .app_not_installed import AppNotInstalledState


class InitialState(State):
    def handle_device(self, device_name : str):
        self.context.device_controller.set_current_device_name(device_name)
        self.context.screen_res = self.context.device_controller.get_screen_resolution()
        #self.context.supplier.set_resolution(self.screen_res)

        if self.context.device_controller.check_app_exists():
            self.context.setState(ReadyState())
        else:
            self.context.setState(AppNotInstalledState())
