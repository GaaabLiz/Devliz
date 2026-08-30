from PySide6.QtCore import QAbstractItemModel, Qt, Signal, QModelIndex
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QFrame, QHeaderView, QStackedWidget
from qfluentwidgets import (
    LineEdit,
    TableView,
    TreeView,
    FluentStyleSheet,
    CommandBar,
    Action,
    FluentIcon,
    TransparentDropDownPushButton,
    CheckableMenu,
    CardWidget,
    BodyLabel,
    ProgressBar,
    CaptionLabel,
    ComboBox,
    RoundMenu,
    MessageBoxBase,
    SubtitleLabel
)
from pylizlib.core.os.snap import QueryType, SearchTarget

from devliz.application.i18n import tr
from devliz.view.util.frame import DevlizQFrame


class CatalogueSearcherView(DevlizQFrame):
    """
    A dialog window for searching within the snapshot catalogue.

    This view provides UI elements for initiating a search, filtering by various
    parameters (target, query type, extensions), and viewing the results in both
    a summary table and a detailed tree view.

    Signals:
        signal_delete_requested(int): Emitted when a user requests to remove a
                                      snapshot from the search list (row index).
        signal_file_double_clicked(str): Emitted when a user double-clicks a file
                                         in the results tree (file path).
    """
    signal_delete_requested = Signal(int)
    signal_file_double_clicked = Signal(str)
    signal_tree_open_parent_folder = Signal(str)
    signal_snapshot_double_clicked = Signal(int)

    def __init__(self, parent=None):
        """
        Initializes the CatalogueSearcherView.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(
            name=tr("Search"), 
            parent=parent, 
            subtitle=tr("Search through the content and files of your snapshots.")
        )

        self.install_label_title()

        content_widget = QWidget(self)
        self.master_layout.addWidget(content_widget)

        # Main layout
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # CommandBar
        self.command_bar = CommandBar(self)
        self.action_start = Action(FluentIcon.SEARCH, tr("Start"), self)
        self.action_stop = Action(FluentIcon.POWER_BUTTON, tr("Stop"), self, enabled=False)

        self.target_button = TransparentDropDownPushButton(tr("Target"), self, FluentIcon.TILES)
        self.target_button.setMenu(self.__create_target_menu())

        self.query_type_button = TransparentDropDownPushButton(tr("Type"), self, FluentIcon.FONT)
        self.query_type_button.setMenu(self.__create_query_type_menu())

        self.extensions_button = TransparentDropDownPushButton(tr("Extensions"), self, FluentIcon.FILTER)
        self.extensions_button.setMenu(self.__create_extensions_menu())

        self.view_button = TransparentDropDownPushButton(tr("View"), self, FluentIcon.VIEW)
        self.view_button.setMenu(self.__create_view_menu())

        self.command_bar.addAction(self.action_start)
        self.command_bar.addAction(self.action_stop)
        self.command_bar.addSeparator()
        self.command_bar.addWidget(self.target_button)
        self.command_bar.addWidget(self.query_type_button)
        self.command_bar.addWidget(self.extensions_button)
        self.command_bar.addSeparator()
        self.command_bar.addWidget(self.view_button)

        # Search bar
        self.search_widget = QWidget(self)
        self.search_layout = QHBoxLayout(self.search_widget)
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_bar = LineEdit(self)
        self.search_bar.setPlaceholderText(tr("Enter the text to search..."))
        self.search_layout.addWidget(self.search_bar)

        # Status Card (initially hidden)
        self.status_card = CardWidget(self)
        status_layout = QVBoxLayout(self.status_card)

        self.status_card_label = BodyLabel(tr("Waiting..."), self.status_card)
        status_layout.addWidget(self.status_card_label)

        # Progress bar
        self.status_card_progress_bar = ProgressBar(self.status_card)
        status_layout.addWidget(self.status_card_progress_bar)

        # Percentage and ETA labels in a new QHBoxLayout below the progress bar
        progress_info_layout = QHBoxLayout()
        self.status_card_percentage_label = CaptionLabel("0%", self.status_card)
        self.status_card_eta_label = CaptionLabel("ETA: --", self.status_card)

        self.status_card_percentage_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_card_eta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        progress_info_layout.addWidget(self.status_card_percentage_label)
        progress_info_layout.addStretch(1)
        progress_info_layout.addWidget(self.status_card_eta_label)
        status_layout.addLayout(progress_info_layout)

        self.status_card.hide()

        # Results table (Snapshot Table)
        self.results_table = TableView(self)
        self.results_table.verticalHeader().hide()
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.column_percents = [0.25, 0.25, 0.15, 0.1625, 0.1875]
        self._distribuisci_colonne_perc()
        self.results_table.resizeEvent = self._table_resize_event
        self.results_table.doubleClicked.connect(self._on_results_table_double_clicked)

        # Tree view (Results List)
        self.tree_view = TreeView(self)
        self.tree_view.doubleClicked.connect(self._on_tree_view_double_clicked)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.setIndentation(20)
        self.tree_view.header().hide()
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_tree_context_menu)
        FluentStyleSheet.TREE_VIEW.apply(self.tree_view)

        # Section X (Stacked Widget for swapping views)
        self.view_stack = QStackedWidget(self)
        self.view_stack.addWidget(self.results_table)
        self.view_stack.addWidget(self.tree_view)

        # Add widgets to main layout
        self.main_layout.addWidget(self.command_bar)
        self.main_layout.addWidget(self.search_widget)
        self.main_layout.addWidget(self.status_card)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.view_stack)

        # Apply Fluent Design stylesheet
        FluentStyleSheet.DIALOG.apply(content_widget)

        # Set initial placeholder
        self._update_search_bar_placeholder()

    def _on_results_table_double_clicked(self, index):
        """
        Handles the double-click event on the results table.
        Emits signal_snapshot_double_clicked with the row index.

        Args:
            index (QModelIndex): The model index of the clicked item.
        """
        if index.isValid():
            self.signal_snapshot_double_clicked.emit(index.row())

    def _on_tree_view_double_clicked(self, index: QModelIndex):
        """
        Handles the double-click event on the results tree view.
        Emits signal_file_double_clicked if a file item is double-clicked.

        Args:
            index (QModelIndex): The model index of the clicked item.
        """
        item = self.tree_view.model().itemFromIndex(index)
        if item and item.parent():  # It's a child item (file path)
            file_path = item.text()
            self.signal_file_double_clicked.emit(file_path)

    def _show_tree_context_menu(self, pos):
        """
        Shows a context menu for items in the results tree.

        Args:
            pos (QPoint): The position where the context menu was requested.
        """
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return

        item = self.tree_view.model().itemFromIndex(index)
        if item and item.parent():  # Only for valid file paths
            file_path = item.text()
            
            menu = RoundMenu(parent=self)
            
            action_open_folder = Action(FluentIcon.FOLDER, tr("Open parent folder"))
            action_open_folder.triggered.connect(lambda: self.signal_tree_open_parent_folder.emit(file_path))
            menu.addAction(action_open_folder)
            
            action_open_file = Action(FluentIcon.DOCUMENT, tr("Open file"))
            action_open_file.triggered.connect(lambda: self.signal_file_double_clicked.emit(file_path))
            menu.addAction(action_open_file)
            
            menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def _show_context_menu(self, pos):
        """
        Shows a context menu for items in the results table.

        Args:
            pos (QPoint): The position where the context menu was requested.
        """
        index = self.results_table.indexAt(pos)
        if not index.isValid():
            return

        menu = RoundMenu(parent=self)
        delete_action = Action(FluentIcon.DELETE, tr("Remove from search"))
        delete_action.triggered.connect(lambda: self.signal_delete_requested.emit(index.row()))
        menu.addAction(delete_action)
        menu.exec(self.results_table.viewport().mapToGlobal(pos))

    def __create_view_menu(self):
        """
        Creates the checkable menu for selecting the view (Snapshot Table vs Results List).

        Returns:
            CheckableMenu: The configured menu for the view button.
        """
        menu = CheckableMenu(parent=self)
        action_group = QActionGroup(self)
        action_group.setExclusive(True)

        self.action_view_snapshot = Action(tr("Snapshot Table"), self, checkable=True)
        self.action_view_results = Action(tr("Results List"), self, checkable=True)

        self.action_view_snapshot.setChecked(True)

        self.action_view_snapshot.triggered.connect(self._on_view_changed)
        self.action_view_results.triggered.connect(self._on_view_changed)

        action_group.addAction(self.action_view_snapshot)
        action_group.addAction(self.action_view_results)

        menu.addAction(self.action_view_snapshot)
        menu.addAction(self.action_view_results)
        return menu

    def _on_view_changed(self):
        """Handles switching between the Snapshot Table and Results List views."""
        if self.action_view_snapshot.isChecked():
            self.view_stack.setCurrentWidget(self.results_table)
        else:
            self.view_stack.setCurrentWidget(self.tree_view)

    def __create_extensions_menu(self):
        """
        Creates the checkable menu for file extension filtering.

        Returns:
            CheckableMenu: The configured menu for the extensions button.
        """
        menu = CheckableMenu(parent=self)

        # Create an action group and allow non-exclusive selection
        action_group = QActionGroup(self)
        action_group.setExclusive(False)

        self.action_ext_txt = Action(".txt", self, checkable=True)
        self.action_ext_log = Action(".log", self, checkable=True)
        self.action_ext_ini = Action(".ini", self, checkable=True)
        self.action_ext_json = Action(".json", self, checkable=True)
        self.action_ext_xml = Action(".xml", self, checkable=True)

        # Set default checked state
        self.action_ext_txt.setChecked(True)
        self.action_ext_log.setChecked(True)
        self.action_ext_ini.setChecked(True)
        self.action_ext_json.setChecked(True)
        self.action_ext_xml.setChecked(True)

        # Add actions to the group
        action_group.addAction(self.action_ext_txt)
        action_group.addAction(self.action_ext_log)
        action_group.addAction(self.action_ext_ini)
        action_group.addAction(self.action_ext_json)
        action_group.addAction(self.action_ext_xml)

        menu.addActions([self.action_ext_txt, self.action_ext_log, self.action_ext_ini, self.action_ext_json, self.action_ext_xml])
        return menu

    def __create_target_menu(self):
        """
        Creates the checkable menu for selecting the search target.

        Returns:
            CheckableMenu: The configured menu for the target button.
        """
        menu = CheckableMenu(parent=self)
        action_group = QActionGroup(self)
        action_group.setExclusive(True)

        self.action_target_map = {}
        target_names = {
            SearchTarget.FILE_NAME: tr("File name"),
            SearchTarget.FILE_CONTENT: tr("File content")
        }
        for target in SearchTarget:
            action = Action(target_names.get(target, target.name.replace("_", " ").title()), self, checkable=True)
            action.setData(target)
            action.triggered.connect(self._update_search_bar_placeholder)
            self.action_target_map[target] = action
            action_group.addAction(action)
            menu.addAction(action)

        # Set default
        self.action_target_map[SearchTarget.FILE_CONTENT].setChecked(True)
        return menu

    def __create_query_type_menu(self):
        """
        Creates the checkable menu for selecting the query type.

        Returns:
            CheckableMenu: The configured menu for the query type button.
        """
        menu = CheckableMenu(parent=self)
        action_group = QActionGroup(self)
        action_group.setExclusive(True)

        self.action_query_type_map = {}
        for query_type in QueryType:
            action = Action(query_type.name.title(), self, checkable=True)
            action.setData(query_type)
            action.triggered.connect(self._update_search_bar_placeholder)
            self.action_query_type_map[query_type] = action
            action_group.addAction(action)
            menu.addAction(action)

        # Set default
        self.action_query_type_map[QueryType.TEXT].setChecked(True)
        return menu

    def _update_search_bar_placeholder(self):
        """Updates the search bar's placeholder text based on the selected search options."""
        target = self.get_selected_search_target()
        query_type = self.get_selected_query_type()

        if target == SearchTarget.FILE_CONTENT and query_type == QueryType.TEXT:
            self.search_bar.setPlaceholderText(tr("Search the content of a file"))
        elif target == SearchTarget.FILE_CONTENT and query_type == QueryType.REGEX:
            self.search_bar.setPlaceholderText(tr("Search the content of a file using a regex"))
        elif target == SearchTarget.FILE_NAME and query_type == QueryType.TEXT:
            self.search_bar.setPlaceholderText(tr("Search the name of a file"))
        elif target == SearchTarget.FILE_NAME and query_type == QueryType.REGEX:
            self.search_bar.setPlaceholderText(tr("Search the name of a file using a regex"))

    def get_selected_extensions(self) -> list[str]:
        """
        Retrieves the list of currently selected file extensions.

        Returns:
            list[str]: A list of selected extension strings (e.g., ['.txt', '.log']).
        """
        extensions = []
        if self.action_ext_txt.isChecked():
            extensions.append(".txt")
        if self.action_ext_log.isChecked():
            extensions.append(".log")
        if self.action_ext_ini.isChecked():
            extensions.append(".ini")
        if self.action_ext_json.isChecked():
            extensions.append(".json")
        if self.action_ext_xml.isChecked():
            extensions.append(".xml")
        return extensions

    def get_selected_query_type(self) -> QueryType:
        """
        Retrieves the currently selected query type.

        Returns:
            QueryType: The selected QueryType enum member.
        """
        for query_type, action in self.action_query_type_map.items():
            if action.isChecked():
                return query_type
        return QueryType.TEXT  # Default fallback

    def get_selected_search_target(self) -> SearchTarget:
        """
        Retrieves the currently selected search target.

        Returns:
            SearchTarget: The selected SearchTarget enum member.
        """
        for target, action in self.action_target_map.items():
            if action.isChecked():
                return target
        return SearchTarget.FILE_CONTENT  # Default fallback

    def set_operation_status(self, active: bool):
        """Sets the UI state based on whether a search operation is active."""
        is_enabled = not active
        self.search_bar.setEnabled(is_enabled)
        self.results_table.setEnabled(is_enabled)
        self.extensions_button.setEnabled(is_enabled)
        self.target_button.setEnabled(is_enabled)
        self.query_type_button.setEnabled(is_enabled)

        if active:
            self.status_card.show()
        else:
            self.status_card.hide()

    def update_status_card(self, text: str, value: int, eta: str = "--"):
        """Updates the status card with text, progress, and ETA."""
        self.status_card_label.setText(text)
        self.status_card_progress_bar.setValue(value)
        self.status_card_percentage_label.setText(f"{value}%")
        self.status_card_eta_label.setText(f"ETA: {eta}")

    def setModel(self, model: QAbstractItemModel):
        """
        Sets the model for the results table.

        Args:
            model (QAbstractItemModel): The table model to set.
        """
        self.results_table.setModel(model)
        self._distribuisci_colonne_perc()

    def _distribuisci_colonne_perc(self):
        """Distributes column widths in the results table based on percentages."""
        total_width = self.results_table.viewport().width()
        if total_width == 0:
            return
        for idx, perc in enumerate(self.column_percents):
            width = int(total_width * perc)
            self.results_table.setColumnWidth(idx, width)

    def _table_resize_event(self, event):
        """Handles the resize event for the results table to redistribute columns."""
        self._distribuisci_colonne_perc()
        super(type(self.results_table), self.results_table).resizeEvent(event)


class SnapshotResultsDialog(MessageBoxBase):
    """
    A dialog that displays search results for a specific snapshot.
    """
    signal_file_double_clicked = Signal(str)
    signal_tree_open_parent_folder = Signal(str)

    def __init__(self, snapshot_name: str, parent=None):
        super().__init__(parent)
        
        self.title_label = SubtitleLabel(tr("Results for: {snapshot}", snapshot=snapshot_name), self)
        self.viewLayout.addWidget(self.title_label)
        
        self.tree_view = TreeView(self)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.setIndentation(20)
        self.tree_view.header().hide()
        
        self.tree_view.doubleClicked.connect(self._on_tree_view_double_clicked)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_tree_context_menu)
        
        self.viewLayout.addWidget(self.tree_view)
        
        self.widget.setMinimumSize(800, 600)
        self.yesButton.hide() # We can hide the yes/no if we want, or keep "Close"
        self.cancelButton.setText(tr("Close"))

    def _on_tree_view_double_clicked(self, index: QModelIndex):
        item = self.tree_view.model().itemFromIndex(index)
        if item and item.parent():
            file_path = item.text()
            self.signal_file_double_clicked.emit(file_path)

    def _show_tree_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return
        item = self.tree_view.model().itemFromIndex(index)
        if item and item.parent():
            file_path = item.text()
            
            menu = RoundMenu(parent=self)
            
            action_open_folder = Action(FluentIcon.FOLDER, tr("Open parent folder"))
            action_open_folder.triggered.connect(lambda: self.signal_tree_open_parent_folder.emit(file_path))
            menu.addAction(action_open_folder)
            
            action_open_file = Action(FluentIcon.DOCUMENT, tr("Open file"))
            action_open_file.triggered.connect(lambda: self.signal_file_double_clicked.emit(file_path))
            menu.addAction(action_open_file)
            
            menu.exec(self.tree_view.viewport().mapToGlobal(pos))