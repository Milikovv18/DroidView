from PyQt6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QComboBox,
    QToolBar,
    QWidget, QLabel, QVBoxLayout, QStackedWidget, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QEvent

from .waitingspinnerwidget import QtWaitingSpinner
from .opengl_scene import QtOpenglDeviceWidget
from general import *


class RootWindow(QMainWindow):
    frontend_signal = pyqtSignal(Notification)

    selection_signal = pyqtSignal(int)
    change_status = pyqtSignal(str)

    def __init__(self, docks, refresh_rate=16, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('UI scrapper')

        # Setting up menu bar
        self.tool_bar = QToolBar("Toolbar")
        self.addToolBar(self.tool_bar)
        self.tool_bar.addAction("&Start", self.stream_start)
        self.tool_bar.addAction("&Capture", self.make_capture)
        self.tool_bar.addAction("S&ave")
        self.tool_bar.addAction("&Load")
        
        self.device_combo_box = QComboBox()
        self.device_combo_box.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.tool_bar.addWidget(self.device_combo_box)

        self.docks = docks
        for window in docks:
            dock = QDockWidget()
            dock.setWindowTitle(window.title)
            dock.setWidget(window)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)


        self.greeting = self.setup_greeting_screen()
        self.app_install = self.setup_app_install_disclaimer()
        self.loading = self.setup_loading_screen()

        self.opengl_scene = QtOpenglDeviceWidget(refresh_rate, self._on_selection)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.loading)
        self.stack.addWidget(self.greeting)
        self.stack.addWidget(self.app_install)
        self.stack.addWidget(self.opengl_scene)
        #self.stack.setCurrentWidget(self.opengl_scene)
        self.setCentralWidget(self.stack)

        self.show()

    def update_content(self, image, nodes, meta):
        self.opengl_scene.update_content(image, nodes, meta)

    def select_node(self, node):
        self.opengl_scene.select_node(node)

    def _on_selection(self, id):
        self.selection_signal.emit(id)

    @pyqtSlot()
    def stream_start(self):
        self.stack.setCurrentWidget(self.loading)
        self.change_status.emit("Waiting for client to connect")

        notification = StreamStartNotification()
        self.frontend_signal.emit(notification)

    @pyqtSlot()
    def make_capture(self):
        self.stack.setCurrentWidget(self.loading)
        self.change_status.emit("Waiting for client to connect")
        
        notification = MakeCaptureNotification()
        self.frontend_signal.emit(notification)

    @pyqtSlot()
    def select_device(self):
        self.stack.setCurrentWidget(self.greeting)
        notification = SelectDeviceNotification(self.device_combo_box.currentText())
        self.frontend_signal.emit(notification)

    @pyqtSlot(Notification)
    def handle_notification(self, notification : Notification):
        match notification:
            case DeviceListReadyNotification():
                if len(notification.adb_names) == 0:
                    return
                
                self.device_combo_box.addItems(notification.adb_names)
                self.device_combo_box.currentTextChanged.connect(self.select_device)

                self.stack.setCurrentWidget(self.greeting)
                notification = SelectDeviceNotification(self.device_combo_box.currentText())
                self.frontend_signal.emit(notification)
            case AppInstallRequiredNotification():
                self.stack.setCurrentWidget(self.app_install)
                pass
            case DeviceReadyNotification():
                # TODO enable start button
                self.stack.setCurrentWidget(self.greeting)
                self.opengl_scene.prepare_for_device(notification.device_resolution)
            case ConnectionEstablishedNotification():
                self.change_status.emit("Waiting for data stream to stabilize")
            case SupplierIsFertileNotification():
                self.stack.setCurrentWidget(self.opengl_scene)
                pass

        #self.propagate_notication(notification)

    def propagate_notication(self, notification):
        self.centralWidget().handle_notification(notification)
        for dock in self.docks:
            dock.handle_notification(notification)


    def keyPressEvent(self, event):
        self.opengl_scene.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.opengl_scene.keyReleaseEvent(event)

    def mousePressEvent(self, event):
        self.opengl_scene.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.opengl_scene.mouseReleaseEvent(event)


    def setup_greeting_screen(self):
        return QLabel("Hello! Connect to device using \"Start\" button!", alignment=Qt.AlignmentFlag.AlignCenter)
    
    def setup_app_install_disclaimer(self):
        container = QWidget()
        layout = QVBoxLayout()
        layout.addStretch()

        disclaimer = QLabel("Looks like the daemon app is not yet installed on target device.\n"
                       "Click the button below to install app automatically.\n"
                       "User interaction might be required depending on manufacturer.\n"
                       "Multiple permissions will be granted to allow usage of screen recording API and accessibility services")
        layout.addWidget(disclaimer)
        
        install_button = QPushButton("Install")
        install_button.pressed.connect(lambda: self.frontend_signal.emit(AppInstallRequestNotification()))
        layout.addWidget(install_button)

        layout.addStretch()
        container.setLayout(layout)
        return container

    def setup_loading_screen(self):
        container = QWidget()
        layout = QVBoxLayout()
        layout.addStretch()

        spinner = QtWaitingSpinner(self, False)
        spinner.setRoundness(70.0)
        spinner.setMinimumTrailOpacity(15.0)
        spinner.setTrailFadePercentage(70.0)
        spinner.setNumberOfLines(12)
        spinner.setLineLength(10)
        spinner.setLineWidth(5)
        spinner.setInnerRadius(10)
        spinner.setRevolutionsPerSecond(1)
        spinner.start()
        layout.addWidget(spinner, 0, Qt.AlignmentFlag.AlignHCenter)

        status_label = QLabel("Initializing...")
        self.change_status.connect(status_label.setText)
        layout.addWidget(status_label, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch()
        container.setLayout(layout)
        return container
