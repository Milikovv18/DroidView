from threading import Thread
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QSurfaceFormat

from general import AdbController, Context
from package_processors import *
from networking import *
from rendering import *


if __name__ == '__main__':
    # Pre-QApplication settings that turned out to be necessary on Linux
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
    fmt = QSurfaceFormat()
    fmt.setVersion(4, 0) # Hardcoded to ensure code stability on my machine
    fmt.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
    QSurfaceFormat.setDefaultFormat( fmt )

    app = QApplication(sys.argv)
    
    tree_window = TreeWindow()
    metadata_window = MetadataWindow()

    root_window = RootWindow([tree_window, metadata_window])

    visualization_proc = VisualizationPackageProcessor()
    tree_proc = TreePackageProcessor()
    meta_proc = PropertyPackageProcessor()

    device_controller = AdbController(
        app_name="com.milikovv.interfacecollector",
        app_host_path=Rf"../android/app/build/outputs/apk/debug/app-debug.apk",
        accessibility_service_name="suppliers.accessibility.AccessibilityServiceService",
        recording_component_name="activities.MainActivity",
        broadcast_component_name="CommandReceiver",
        broadcast_intent="com.interfacecollector.intent.COMMAND"
    )

    proc_manager = ProcessManager(
        Context(device_controller),
        [
            ProcWindowBundle(visualization_proc, root_window),
            ProcWindowBundle(tree_proc, tree_window),
            ProcWindowBundle(meta_proc, metadata_window)
        ]
    )

    # Connect frontend and backend
    root_window.frontend_signal.connect(proc_manager.handle_notification)
    proc_manager.backend_signal.connect(root_window.handle_notification)

    Thread(target=proc_manager.post_init()).start()

    sys.exit(app.exec())
