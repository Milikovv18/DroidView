from .state import State
from .active import StreamingState, CapturingState


class ReadyState(State):
    def is_app_installed(self) -> bool:
        return True

    def start_stream(self):
        # Start RTMP server
        self.context.device_controller.request_transmission("VIDEO_DRIVEN")

        self.context.setState(StreamingState())

    def capture(self):
        # Start TCP server
        self.context.device_controller.request_transmission("ACCESSIBILITY_DRIVEN")

        self.context.setState(CapturingState())
