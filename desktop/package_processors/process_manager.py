from dataclasses import dataclass
from threading import Thread
import time

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget

from networking import *
from general import *


@dataclass
class ProcWindowBundle:
    proc: None # No inheritance
    window: QWidget


class ProcessManager(QObject):
    backend_signal = pyqtSignal(Notification)
    active_thread = None

    def __init__(self, context : Context, proc_win_bundles : list[ProcWindowBundle]) -> None:
        super().__init__()
        self.context = context
        self.bundles = proc_win_bundles
        self.node_id = 0

        for bundle in self.bundles:
            if hasattr(bundle.window, "request_selection"):
                bundle.window.request_selection.connect(self.request_selection)

    # Called after all signal-slot connections are established
    def post_init(self):
        self.backend_signal.emit(DeviceListReadyNotification(self.context.device_controller.get_connected_devices()))

    def run(self):
        #while not self.supplier.is_ready():
        #    time.sleep(1)

        self.backend_signal.emit(ConnectionEstablishedNotification())

        #while True:
        #    data = self.context.get_data()
        #    if data.nodes is not None and data.pixels is not None:
        #        break

        self.backend_signal.emit(SupplierIsFertileNotification())

        try:
            while True:
                self.node_id = 0
                data = self.context.get_data()

                self.matrix = [[] for _ in range(len(self.bundles))]
                self.convert_recursive([data.nodes])

                # TODO Late metadata is not requested when percussion is not active
                for i, bundle in enumerate(self.bundles):
                    bundle.window.update_content(data.pixels, self.matrix[i], bundle.proc.get_stats())
        except SupplierClosedException as _:
            self.active_thread = None

    def convert_recursive(self, nodes, level=1):
        result = [[] for _ in range(len(self.bundles))]
        for node in nodes:
            children = [[] for _ in range(len(self.bundles))]
            if "children" in node:
                children = self.convert_recursive(node["children"], level+1)

            for i, bundle in enumerate(self.bundles):
                typed_node = bundle.proc.convert(self.node_id, node, level, children[i])
                result[i].append(typed_node)
                self.matrix[i].append(typed_node)
            self.node_id += 1
        return result
    
    @pyqtSlot(int)
    def request_selection(self, id):
        for i, bundle in enumerate(self.bundles):
            bundle.window.select_node(self.matrix[i][id])

    @pyqtSlot(Notification)
    def handle_notification(self, notification : Notification):
        match notification:
            case SelectDeviceNotification():
                self.context.handle_device(notification.device_name)
                
                for bundle in self.bundles:
                    if hasattr(bundle.proc, "set_dims"):
                        bundle.proc.set_dims(self.context.screen_res)

                if self.context.is_app_installed():
                    self.backend_signal.emit(DeviceReadyNotification(self.context.screen_res))
                else:
                    self.backend_signal.emit(AppInstallRequiredNotification())

            case AppInstallRequestNotification():
                self.context.install_app()
                self.backend_signal.emit(DeviceReadyNotification(self.context.screen_res))
            case StreamStartNotification():
                self.context.start_stream()
                if self.active_thread is None:
                    self.active_thread = Thread(target=self.run, daemon=True).start()
            case MakeCaptureNotification():
                self.context.capture()
                if self.active_thread is None:
                    self.active_thread = Thread(target=self.run, daemon=True).start()
    