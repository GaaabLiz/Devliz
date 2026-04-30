from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import BodyLabel, TableView

from devliz.application.i18n import tr
from devliz.view.util.frame import DevlizQFrame


class ActionHistoryTableModel(QAbstractTableModel):

    def __init__(self):
        super().__init__()
        self._rows: list[dict[str, str]] = []
        self._headers = [tr("Timestamp"), tr("Screen"), tr("Action"), tr("Details")]

    def set_rows(self, rows: list[dict[str, str]]):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 4

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._headers):
            return self._headers[section]
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        row = self._rows[index.row()]
        col = index.column()
        if col == 0:
            return row.get("created_at", "")
        if col == 1:
            return tr(row.get("screen_key", ""))
        if col == 2:
            return tr(row.get("action_key", ""))
        if col == 3:
            return row.get("details", "")
        return None


class ActionHistoryView(DevlizQFrame):

    def __init__(self, parent=None):
        super().__init__(name=tr("Action History"), parent=parent)
        self.model = ActionHistoryTableModel()
        self.__setup_ui()

    def __setup_ui(self):
        self.install_label_title()

        self.empty_label = BodyLabel(tr("No actions recorded yet."), self)
        self.table = TableView(self)
        self.table.setModel(self.model)
        self.table.verticalHeader().hide()
        self.table.setWordWrap(False)

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(10)
        container_layout.addWidget(self.empty_label)
        container_layout.addWidget(self.table)

        self.master_layout.addLayout(container_layout)
        self.master_layout.addStretch(1)

    def update_rows(self, rows: list[dict[str, str]]):
        self.model.set_rows(rows)
        self.empty_label.setVisible(len(rows) == 0)
