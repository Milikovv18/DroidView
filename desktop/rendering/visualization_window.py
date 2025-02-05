from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QObject, pyqtSlot

from package_processors.tree_processor import TreeItem
from .waitingspinnerwidget import QtWaitingSpinner
from .opengl_scene import QtOpenglDeviceWidget
from general import *


class VisualizationWindow(QWidget, QObject):
    title = "Visualization"
    selection_signal = pyqtSignal(int)
    change_status = pyqtSignal(str)
    update_signal = pyqtSignal(TreeItem)

    def __init__(self, refresh_period = 33, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.greeting = self.setup_greeting_screen()
        self.app_install = self.setup_app_install_disclaimer()
        self.loading = self.setup_loading_screen()

        self.opengl_scene = QtOpenglDeviceWidget(refresh_period, self._on_selection)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.greeting)
        self.stack.addWidget(self.app_install)
        self.stack.addWidget(self.loading)
        self.stack.addWidget(self.opengl_scene)

        layout = QHBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def handle_notification(self, notification : Notification):
        match notification:
            case AppInstallRequiredNotification():
                self.stack.setCurrentWidget(self.app_install)
            case StreamStartNotification():
                self.stack.setCurrentWidget(self.loading)
                self.change_status.emit("Waiting for client to connect")
            case ConnectionEstablishedNotification():
                self.change_status.emit("Waiting for data stream to stabilize")
            case SupplierIsFertileNotification():
                self.stack.setCurrentWidget(self.opengl_scene)

    def update_content(self, image, nodes : TreeItem, meta):
        self.opengl_scene.update_content(image, nodes, meta)

    def select_node(self, node : TreeItem):
        self.opengl_scene.select_node(node)

    def _on_selection(self, id):
        self.selection_signal.emit(id)

    def eventFilter(self, object, event):
        # Mouse events
        if event.type() == QEvent.Type.MouseButtonPress:
            self.opengl_scene.mousePressEvent(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self.opengl_scene.mouseReleaseEvent(event)
        
        # Keyboard events
        elif event.type() == QEvent.Type.KeyPress:
            self.opengl_scene.keyPressEvent(event)
        elif event.type() == QEvent.Type.KeyRelease:
            self.opengl_scene.keyReleaseEvent(event)
        
        return super().eventFilter(object, event)


    def setup_greeting_screen(self):
        return QLabel("Hello!", alignment=Qt.AlignmentFlag.AlignCenter)
    
    def setup_app_install_disclaimer(self):
        container = QWidget()
        layout = QVBoxLayout()
        layout.addStretch()

        disclaimer = QLabel("Looks like the daemon app is not yet installed on target device.\n"
                       "Click the button below to install app automatically.\n"
                       "Multiple permissions will be granted to allow usage of screen recording API and accessibility services")
        layout.addWidget(disclaimer)
        
        install_button = QPushButton("Install")
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

        status_label = QLabel("Waiting for client to connect")
        self.change_status.connect(status_label.setText)
        layout.addWidget(status_label, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch()
        container.setLayout(layout)
        return container
