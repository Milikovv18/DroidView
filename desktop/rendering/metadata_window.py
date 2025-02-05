from dataclasses import asdict
import time

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QTableView, QHeaderView, QStackedWidget
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QAbstractTableModel, pyqtSlot, pyqtSignal

from package_processors.property_processor import PropertiesLayout
from general import *


class MetadataWindow(QWidget):
    title = "Node info"
    no_data_sign = "Select node to view its properties"
    update_signal = pyqtSignal(PropertiesLayout)
    min_update_interval = 1#sec

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_label = QLabel(self.no_data_sign, alignment=Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)

        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().hide()
        self.table.hide()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty_label)
        self.stack.addWidget(self.table)

        layout = QHBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.update_signal.connect(self.update_content_qt_thread, Qt.ConnectionType.QueuedConnection)

    def handle_notification(self, notification : Notification):
        pass

    last_update_time = 0
    def update_content(self, _, nodes : PropertiesLayout, __):
        if self.last_update_time < time.time() - self.min_update_interval:
            self.update_signal.emit(nodes[-1])
            self.last_update_time = time.time()

    @pyqtSlot(PropertiesLayout)
    def update_content_qt_thread(self, root_node : PropertiesLayout):
        self.build_recursive(root_node.children)
        self.select_node(root_node)

        self.table.show()
        self.empty_label.hide()

    def select_node(self, node):
        self.render_single_node(node)

    def render_single_node(self, node):
        self.model = TableModel([[key, value] for key, value in asdict(node).items()])
        self.table.setModel(self.model)

    flat = []
    def build_recursive(self, nodes : list[PropertiesLayout]):
        for node in nodes:
            self.flat.append([[key, value] for key, value in asdict(node).items()])
            self.build_recursive(node.children)


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])