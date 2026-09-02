from PySide6.QtWidgets import QVBoxLayout, QHeaderView
from qfluentwidgets import BodyLabel, TableView

from devliz.application.i18n import tr
from devliz.view.util.frame import DevlizQFrame
from devliz.model.action_history import ActionHistoryTableModel


class ActionHistoryView(DevlizQFrame):

    def __init__(self, parent=None):
        super().__init__(
            name=tr("Action History"), 
            parent=parent, 
            subtitle=tr("View a detailed log of all your actions in the application.")
        )
        self.layout = self.get_scroll_layout()
        self.model = ActionHistoryTableModel()
        self.__setup_ui()

    def __setup_ui(self):
        self.install_label_title()

        self.empty_label = BodyLabel(tr("No actions recorded yet."), self)
        self.table = TableView(self)
        self.table.setModel(self.model)
        self.table.verticalHeader().hide()
        self.table.setWordWrap(False)
        
        # Fai in modo che la tabella occupi tutto lo spazio orizzontale
        # e che l'intestazione non appaia tagliata ai lati.
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        container_layout.addWidget(self.empty_label)
        container_layout.addWidget(self.table, 1)

        self.master_layout.addLayout(container_layout, 1)

    def update_rows(self, rows: list[dict[str, str]]):
        self.model.set_rows(rows)
        self.empty_label.setVisible(len(rows) == 0)
