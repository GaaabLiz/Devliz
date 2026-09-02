from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidgetItem, QFileDialog, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem, QVBoxLayout
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import FluentIcon, PushButton, Action, RoundMenu, ListWidget

from devliz.application.i18n import tr


class TabDirectories(QWidget):
    """
    A widget representing the directories tab within the snapshot configuration dialog.
    It allows the user to add, remove, and manage the list of directories associated
    with a snapshot, including adding starred/favorite directories.
    """

    Signal_btn_add_dir = Signal(str)
    Signal_btn_choose_dir = Signal()
    signal_data_changed = Signal(bool)

    def __init__(
            self,
            payload_data: Snapshot | None = None,
            starred_dirs: list[Path] = []
    ):
        """
        Initializes the TabDirectories widget.

        Args:
            payload_data (Snapshot | None, optional): An existing snapshot whose directories 
                should be loaded for editing. Defaults to None.
            starred_dirs (list[Path], optional): A list of favorite directory paths 
                that can be quickly added. Defaults to [].
        """
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.directories: list[Path] = []
        self.starred_dirs_paths = [p.__str__() for p in starred_dirs]
        self.payload_data: Snapshot | None = payload_data

        # Widget
        self.listWidget = ListWidget(self)
        self.listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.__show_context_menu)
        self.btn_widget = self.__get_btn_widget()

        # Aggiungo i widget al layout
        self.layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.btn_widget)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.listWidget)
        self.layout.addStretch()

        self.Signal_btn_add_dir.connect(self.__on_add_directory_request)
        self.Signal_btn_choose_dir.connect(self.__on_add_directory_request)

        # Se sono in edit mode, popolo la lista
        if self.payload_data:
            for dir_assoc in self.payload_data.directories:
                self.add_directory(Path(dir_assoc.original_path), execute_checks=False)
            self._capture_initial_directories_state()

    # AGGIUNTO: Metodo per catturare lo stato iniziale delle directory
    def _capture_initial_directories_state(self):
        """
        Captures the initial state of the selected directories to enable tracking of subsequent modifications.
        """
        self._initial_directories = set(str(d) for d in self.directories)

    # AGGIUNTO: Metodo per verificare se ci sono state modifiche
    def _check_directories_changed(self):
        """
        Checks if the current list of directories differs from the initial state captured.
        Emits the signal_data_changed signal with True if changed, otherwise False.

        Returns:
            None
        """
        if not hasattr(self, '_initial_directories'):
            # Se non c'è stato iniziale, considera modificato se ci sono directory
            return len(self.directories) > 0

        current_directories = set(str(d) for d in self.directories)
        changed = current_directories != self._initial_directories
        self.signal_data_changed.emit(changed)
        return None

    def __show_context_menu(self, pos):
        """
        Displays a context menu when right-clicking on an item in the directory list.
        The menu allows for deleting the selected directory from the list.

        Args:
            pos (QPoint): The position where the context menu was requested.
        """
        item = self.listWidget.itemAt(pos)
        if item is not None:
            menu = RoundMenu()
            action_delete = Action(FluentIcon.DELETE, tr("Delete"),
                                   triggered=lambda: self.__delete_selected_item(item))
            menu.addAction(action_delete)
            global_pos = self.listWidget.mapToGlobal(pos)
            menu.exec(global_pos)

    def __get_btn_widget(self):
        """
        Creates and returns the widget containing the buttons for adding directories.
        Includes a standard 'Add folder' button and a dropdown button for starred folders.

        Returns:
            QWidget: The container widget with the action buttons.
        """
        btn_container = QWidget(self)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()  # spazio a sinistra

        self.btn_choose_dir = PushButton(tr("Add folder"), self, FluentIcon.FOLDER_ADD)
        self.btn_choose_dir.setMaximumWidth(300)
        self.btn_choose_dir.clicked.connect(lambda: self.Signal_btn_choose_dir.emit())
        btn_layout.addWidget(self.btn_choose_dir)

        self.btn_choose_dir_starred = UiUtils.create_widget_act_bar_btn(
            self,
            self.starred_dirs_paths,
            tr("Add starred folder"),
            FluentIcon.FOLDER_ADD,
            False,
            self.Signal_btn_add_dir,
            FluentIcon.FOLDER
        )
        self.btn_choose_dir_starred.setMaximumWidth(300)
        btn_layout.addWidget(self.btn_choose_dir_starred)
        btn_layout.addStretch()  # spazio a destra
        return btn_container

    def __on_add_directory_request(self, path: str | None = None):
        """
        Slot triggered when a directory addition is requested.
        If a path is provided (e.g. from the starred folders dropdown), it adds it directly.
        If no path is provided, it opens a file dialog for the user to select one.

        Args:
            path (str | None, optional): The pre-selected path to add. Defaults to None.
        """
        if path is None:
            dir_path = QFileDialog.getExistingDirectory(self, tr("Select a folder to add to the list"), )
            if dir_path:
                self.add_directory(Path(dir_path))
            else:
                return
        else:
            self.add_directory(Path(path))

    def add_directory(self, directory: Path, execute_checks: bool = True):
        """
        Adds a directory to the local list and updates the UI.
        Can optionally perform validation checks before adding.

        Args:
            directory (Path): The path object of the directory to add.
            execute_checks (bool, optional): If True, checks for duplicates and path validity. 
                Defaults to True.
        """
        if execute_checks:
            if directory in self.directories:
                UiUtils.show_message(tr("Warning"), tr("The selected folder is already in the list."), self)
                return
            if not directory.exists():
                UiUtils.show_message(tr("Warning"), tr("The selected folder does not exist on the system."), self)
                return
            if not directory.is_dir():
                UiUtils.show_message(tr("Warning"), tr("The selected folder is not a valid folder."), self)
                return
        self.directories.append(directory)
        item = QListWidgetItem(directory.__str__())
        self.listWidget.addItem(item)

        if execute_checks:
            self._check_directories_changed()

    def __delete_selected_item(self, item: QListWidgetItem):
        """
        Deletes the selected list widget item and its corresponding directory from the internal list.

        Args:
            item (QListWidgetItem): The item representing the directory to remove.
        """
        dir_path = Path(item.text())
        if dir_path in self.directories:
            self.directories.remove(dir_path)
        self.listWidget.takeItem(self.listWidget.row(item))
        self._check_directories_changed()