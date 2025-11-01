from pathlib import Path

from PySide6.QtCore import Signal, Qt, QMargins
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QHBoxLayout, QWidget, QTableWidgetItem, QHeaderView
from pylizlib.core.os.snap import Snapshot, SnapshotSortKey, SnapshotUtils
from pylizlib.qt.util.ui import UiUtils
from qfluentwidgets import SearchLineEdit, Action, FluentIcon, CommandBar, TableWidget, setFont, BodyLabel, RoundMenu, \
    TransparentDropDownPushButton, CheckableMenu, MenuIndicatorType

from devliz.application.app import app_settings, AppSettings
from devliz.domain.data import DevlizData, DevlizSnapshotData
from devliz.view.util.frame import DevlizQFrame



class SnapshotCatalogueWidget(DevlizQFrame):

    signal_import_requested = Signal()
    signal_sort_requested = Signal(SnapshotSortKey)
    signal_edit_requested = Signal(Snapshot)
    signal_install_requested = Signal(Snapshot)
    signal_delete_requested = Signal(Snapshot)
    signal_open_folder_requested = Signal(Path)
    signal_update_dirs_to_locals_requested = Signal()
    signal_duplicate_requested = Signal(Snapshot)
    signal_search_internal_content_all = Signal()
    signal_search_internal_content_single = Signal(Snapshot)


    def __init__(self, parent=None):
        super().__init__(name="Catalogo", parent=parent)

        # Inizializzo le variabili
        self._all_data: list[Snapshot] = []
        self.filtered: list[Snapshot] = []
        self.is_filtered: bool = False
        self.current_selected: Snapshot | None = None

        # Aggiungo i widgets
        self.__setup_label()
        self.__setup_action_bar()
        self.__setup_table()
        self.__setup_footer()

    def __setup_label(self):
        self.master_layout.addWidget(self.get_label_title())

    def __setup_action_bar(self):
        self.search_line_edit = SearchLineEdit(self)
        self.search_line_edit.textChanged.connect(self._text_changed_filter)

        self.action_import = Action(FluentIcon.ADD, 'Importa', triggered=lambda: self.signal_import_requested.emit())
        self.action_edit = Action(FluentIcon.EDIT, 'Modifica', enabled=False, triggered=lambda: self.signal_edit_requested.emit())

        menu_combobox_sort = TransparentDropDownPushButton("Ordina", self, FluentIcon.SCROLL)
        menu_combobox_sort.setMenu(self.__get_sort_menu())
        menu_combobox_sort.setFixedHeight(34)

        self.action_search_internal_all = Action(FluentIcon.SEARCH, "Cerca contenuto", triggered=lambda: self.signal_search_internal_content_all.emit())

        left_command_bar = CommandBar()
        left_command_bar.setMinimumWidth(600)
        left_command_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        left_command_bar.addAction(self.action_import)
        left_command_bar.addAction(self.action_search_internal_all)
        left_command_bar.addWidget(menu_combobox_sort)
        # left_command_bar.addSeparator()
        # left_command_bar.addAction(self.action_edit)

        lay = QHBoxLayout()
        lay.addWidget(left_command_bar)  # Sinistra
        lay.addStretch(1)  # Riempie lo spazio centrale
        lay.addWidget(self.search_line_edit)  # Destra

        container = QWidget()
        container.setLayout(lay)

        self.master_layout.addWidget(container)

    def __get_sort_menu(self, pos=None):
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)

        action_sort_name = Action(FluentIcon.QUICK_NOTE, "Nome", checkable=True, triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.NAME))
        action_sort_author = Action(FluentIcon.PEOPLE, "Autore", checkable=True, triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.AUTHOR))
        action_sort_date_create = Action(FluentIcon.CALENDAR, "Data creazione", checkable=True, triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.DATE_CREATED))
        action_sort_date_modify = Action(FluentIcon.EDIT, "Data modifica", checkable=True, triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.DATE_MODIFIED))

        action_sort_group = QActionGroup(self)
        action_sort_group.addAction(action_sort_name)
        action_sort_group.addAction(action_sort_author)
        action_sort_group.addAction(action_sort_date_create)
        action_sort_group.addAction(action_sort_date_modify)

        menu.addActions([
            action_sort_name,
            action_sort_author,
            action_sort_date_create,
            action_sort_date_modify
        ])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu

    def __setup_table(self, data: list[Snapshot] | None = None):
        self._all_data = data if data is not None else []
        if data is None:
            data = []
        self.table = TableWidget(self)

        # Enable border and set rounded corners
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)

        self.table.setWordWrap(False)
        self.table.setColumnCount(6)
        self.table.setRowCount(len(data))

        snap_custom_data = app_settings.get(AppSettings.snap_custom_data)
        for i, config in enumerate(data):
            sttt = config.get_for_table_array(snap_custom_data)
            for j in range(6):
                temp = sttt[j]
                item = QTableWidgetItem(temp)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, j, item)

        self.table.itemDoubleClicked.connect(self._on_table_item_double_clicked)

        selection_model = self.table.selectionModel()
        selection_model.selectionChanged.connect(self._on_item_selection_changed)

        # Set horizontal header and hide vertical header
        headers = []
        headers.append("Nome")
        headers.append("Descrizione")
        for i in snap_custom_data:
            headers.append(i)
        headers.append("Data/Ora")
        headers.append("Tags")
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().hide()

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Percentuali colonne somma a 1.0
        self.column_percents = [0.20, 0.25, 0.10, 0.10, 0.18, 0.17]

        # Chiama il metodo per ridistribuire larghezze in pixel
        self._distribuisci_colonne_perc()

        # Connetto resizeEvent (override) per aggiornare larghezze dinamicamente
        self.table.resizeEvent = self._table_resize_event


        self.master_layout.addWidget(self.table)


    def __setup_footer(self, count: int = 0, size: str = "0"):
        lay = QHBoxLayout()
        left_label = BodyLabel(app_settings.get(AppSettings.catalogue_path), self)
        setFont(left_label, 12)
        left_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        right_label = BodyLabel(f"Totale configurazioni: {count} ({size})", self)
        setFont(right_label, 12)
        right_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        lay.addWidget(left_label)
        lay.addStretch(1)
        lay.addWidget(right_label)

        lay.setContentsMargins(QMargins(5, 0, 5, 0))

        container = QWidget(self)
        container.setLayout(lay)
        self.master_layout.addWidget(container)


    def _show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        if 0 <= row < len(self.__get_actual_data()):
            config = self.__get_actual_data()[row]
            print(config)
        else:
            return

        menu = RoundMenu()
        menu.addAction(Action(FluentIcon.DOWN, "Installa", triggered=lambda: self.signal_install_requested.emit(config)))
        menu.addAction(Action(FluentIcon.EDIT, "Modifica", triggered=lambda: self.signal_edit_requested.emit(config)))
        #menu.addAction(Action(FluentIcon.UPDATE, "Aggiorna cartelle", triggered=lambda: self.signal_update_dirs_to_locals_requested.emit(config)))
        menu.addAction(Action(FluentIcon.DICTIONARY_ADD, "Duplica", triggered=lambda: self.signal_duplicate_requested.emit(config)))
        menu.addAction(Action(FluentIcon.DELETE, "Cancella", triggered=lambda: self.signal_delete_requested.emit(config)))
        global_pos = self.table.viewport().mapToGlobal(pos)
        menu.exec(global_pos)

    def _on_table_item_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        # Recupera il dato associato da self._all_data (lista originale filtrata o totale)
        # Se usi la tabella filtrata devi adattare la logica per avere la lista filtrata in quel momento
        if 0 <= row < len(self.__get_actual_data()):
            config = self.__get_actual_data()[row]
            # Chiama il tuo metodo con l’oggetto selezionato
            self.signal_open_folder_requested.emit(config)

    def _on_item_selection_changed(self):
        selected_indexes = self.table.selectionModel().selectedIndexes()
        has_selection = len(selected_indexes) > 0
        self.action_edit.setEnabled(has_selection)

        # if has_selection:
        #     row = selected_indexes[0].row()  # prendo la prima selezione
        #     if 0 <= row < len(self._all_data):
        #         obj = self._all_data[row]
        #         # Qui puoi usare obj come vuoi
        #         print(f'Elemento selezionato: {obj}')

    def _distribuisci_colonne_perc(self):
        total_width = self.table.viewport().width()
        for idx, perc in enumerate(self.column_percents):
            width = int(total_width * perc)
            self.table.setColumnWidth(idx, width)

    def _table_resize_event(self, event):
        # Richiamo la ridistribuzione proporzionale delle colonne
        self._distribuisci_colonne_perc()
        # Rilancio il resize base per far continuare l’evento
        super(type(self.table), self.table).resizeEvent(event)

    def _text_changed_filter(self, text: str):
        text = text.lower().strip()
        if not text:
            self.filtered = self._all_data  # se ricerca vuota, mostra tutto
            self.is_filtered = False
        else:
            self.filtered = []
            self.is_filtered = True
            for config in self._all_data:
                custom_data: dict[str, str] = config.data if config.data is not None else {}
                if (text in config.name.lower() or
                    text in config.desc.lower() or
                    any(text in tag.lower() for tag in config.tags) or
                    any(text in str(value).lower() for value in custom_data.values())):
                    self.filtered.append(config)
        self.__update_table_data(self.filtered)

    def __get_actual_data(self) -> list[Snapshot]:
        if self.is_filtered:
            return self.filtered
        return self._all_data

    def __update_table_data(self, data: list[Snapshot]):
        # Pulisce e reinserisce i dati filtrati nella tabella
        self.table.setRowCount(len(data))
        custom_data = app_settings.get(AppSettings.snap_custom_data)
        for i, config in enumerate(data):
            sttt = config.get_for_table_array(custom_data)
            for j in range(6):
                item = QTableWidgetItem(str(sttt[j]))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, j, item)

        # Aggiorna colonne e layout se serve
        self._distribuisci_colonne_perc()

    def sort(self, method: SnapshotSortKey):
        self.search_line_edit.clear()
        self._all_data = SnapshotUtils.sort_snapshots(self.__get_actual_data(), method)
        self.__update_table_data(self._all_data)

    def update_widget(self, snapshot_data: DevlizSnapshotData):
        UiUtils.clear_layout(self.master_layout)
        self.__setup_label()
        self.__setup_action_bar()
        self.__setup_table(snapshot_data.snapshot_list)
        self.__setup_footer(snapshot_data.count, snapshot_data.get_mb_size)