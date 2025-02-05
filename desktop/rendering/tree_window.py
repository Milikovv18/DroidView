import time

from PyQt6.QtCore import Qt, QModelIndex, QAbstractItemModel, pyqtSlot, pyqtSignal, QItemSelection, QItemSelectionModel
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QTreeView, QStackedWidget

from package_processors.tree_processor import TreeItem
from .waitingspinnerwidget import QtWaitingSpinner
from general import *


class TreeModelWithIndices(QAbstractItemModel):
    def __init__(self, root_node):
        super(TreeModelWithIndices, self).__init__(None)
        self.rootItem = root_node

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.ItemDataRole.UserRole:
            return item
        if role == Qt.ItemDataRole.DisplayRole:
            return item.data
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ["A"][section]
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.childItems[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        parentItem = index.internalPointer().parentItem
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return len(parentItem.childItems)
    
    def invisibleRootItem(self):
        return self.rootItem


class TreeWindow(QWidget):
    title = "Hierarchy"
    no_data_sign = "Make a capture to view windows and nodes"
    update_signal = pyqtSignal(TreeItem)
    selection_signal = pyqtSignal(int)
    min_update_interval = 1#sec

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.spinner = self.setup_spinner()

        self.empty_label = QLabel(self.no_data_sign, alignment=Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)

        self.tree_view = QTreeView()
        self.tree_view.hide()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty_label)
        self.stack.addWidget(self.tree_view)

        layout = QHBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.update_signal.connect(self.update_content_qt_thread, Qt.ConnectionType.QueuedConnection)

    def handle_notification(self, notification : Notification):
        pass

    last_update_time = 0
    def update_content(self, _, nodes : TreeItem, __):
        if self.last_update_time < time.time() - self.min_update_interval:
            self.update_signal.emit(nodes[-1])
            self.last_update_time = time.time()

    @pyqtSlot(TreeItem)
    def update_content_qt_thread(self, root_node : TreeItem):
        self.build_recursive([root_node], None)
        self.model = TreeModelWithIndices(root_node)
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection)

        self.layout().replaceWidget(self.spinner, self.tree_view)

    def build_recursive(self, nodes : list[TreeItem], parent):
        for node in nodes:
            node.set_parent(parent)
            self.build_recursive(node.childItems, node)

    def select_node(self, node : TreeItem):
        index = self.model.createIndex(node.row(), 0, node)
        self.tree_view.selectionModel().select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_selection(self, selected : QItemSelection, deselected : QItemSelection):
        index = selected.indexes()[0]
        item : TreeItem = self.tree_view.model().data(self.tree_view.model().index(index.row(), index.column(), index.parent()), Qt.ItemDataRole.UserRole)
        self.selection_signal.emit(item.id)

    def setup_spinner(self):
        spinner = QtWaitingSpinner(self)
        spinner.setRoundness(70.0)
        spinner.setMinimumTrailOpacity(15.0)
        spinner.setTrailFadePercentage(70.0)
        spinner.setNumberOfLines(12)
        spinner.setLineLength(10)
        spinner.setLineWidth(5)
        spinner.setInnerRadius(10)
        spinner.setRevolutionsPerSecond(1)
        spinner.start()
        return spinner
