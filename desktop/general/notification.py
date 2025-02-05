from dataclasses import dataclass, field


def description(msg):
    return field(default=msg, repr=False, init=False)


@dataclass
class Notification:
    msg : str

    def __post_init__(self):
        print(self.__class__.__name__, self.__dict__)


@dataclass
class DeviceListReadyNotification(Notification):
    msg : str = description("Got list of connected devices")
    adb_names : list[str]


@dataclass
class SelectDeviceNotification(Notification):
    msg : str = description("Device selected")
    device_name : str


@dataclass
class AppInstallRequiredNotification(Notification):
    msg : str = description("App installation is required")


@dataclass
class AppInstallRequestNotification(Notification):
    msg : str = description("Request app installation")
    

@dataclass
class DeviceReadyNotification(Notification):
    msg : str = description("Daemon app is installed and device is ready")
    device_resolution : tuple[int, int]


# StreamStopNotification == MakeCaptureNotification
@dataclass
class StreamStartNotification(Notification):
    msg : str = description("Start stream")
    

@dataclass
class MakeCaptureNotification(Notification):
    msg : str = description("Capture current device state")
    

@dataclass
class ConnectionEstablishedNotification(Notification):
    msg : str = description("Client connected")
    

@dataclass
class SupplierIsFertileNotification(Notification):
    msg : str = description("Data stream stabilized")
    