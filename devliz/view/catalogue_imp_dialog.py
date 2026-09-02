import re

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import FluentStyleSheet, PushButton, PrimaryPushButton

from devliz.domain.data import DevlizData
from devliz.view.catalogue_imp_tabs import DialogConfigTabs
from devliz.application.i18n import tr


class DialogConfig(QDialog):
    """
    Dialog window for creating or editing a snapshot configuration.
    It contains tabs for detailed information and associated directories.
    """

    signal_payload = Signal(dict, bool)

    def __init__(
            self,
            devliz_data: DevlizData,
            edit_mode: bool = False,
            edit_data: Snapshot | None = None,
            parent=None
    ):
        """
        Initialize the DialogConfig window.

        :param devliz_data: Core data access object for the application.
        :param edit_mode: True if editing an existing snapshot, False for creating a new one.
        :param edit_data: The snapshot data to edit, required if edit_mode is True.
        :param parent: The parent widget.
        """
        super().__init__(parent)

        # Initialize variables
        self.edit_mode = edit_mode
        self.edit_data: Snapshot | None = edit_data
        self.devliz_data = devliz_data
        self.output_data: dict | None = None

        # Global dialog settings
        self.setWindowTitle(self.__get_dialog_text())
        self.resize(900, 550)

        # Global layout settings
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.setContentsMargins(50, 0, 50, 50)
        self.layout.setSpacing(30)

        # Create widgets
        self.__tabs = DialogConfigTabs(self.devliz_data, self.edit_data)
        self.__btn_layout = self.__get_btn_layout()

        # Track combined modification state
        self._form_modified = False
        self._directories_modified = False

        # Connect signals from tabs
        self.__tabs.tab_details.signal_data_changed.connect(self._on_form_changed)
        self.__tabs.tab_directories.signal_data_changed.connect(self._on_directories_changed)

        # Add widgets to layout
        self.layout.addWidget(self.__tabs)
        self.layout.addLayout(self.__btn_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def __get_dialog_text(self):
        """
        Determine the appropriate title text for the dialog based on its current mode.

        :return: A localized string for the dialog title.
        """
        if not self.edit_mode:
            return tr("Import")
        config_name = self.edit_data.name if self.edit_data else ""
        return tr("Edit a configuration") + (f": {config_name}" if config_name else "")

    def _on_form_changed(self, changed: bool):
        """
        Handle modification state changes from the details form.

        :param changed: True if the form data has been modified.
        """
        self._form_modified = changed
        self._update_button_state()

    def _on_directories_changed(self, changed: bool):
        """
        Handle modification state changes from the directories tab.

        :param changed: True if the directories data has been modified.
        """
        self._directories_modified = changed
        self._update_button_state()

    def _update_button_state(self):
        """
        Update the enabled state of the create/save button based on form and directories modifications.
        The button is enabled if there are modifications in either the form OR the directories.
        """
        enabled = self._form_modified or self._directories_modified
        self.btn_create.setEnabled(enabled)

    def __get_btn_layout(self):
        """
        Create and configure the button layout for accepting or rejecting the dialog.

        :return: A QVBoxLayout containing the primary action buttons.
        """
        # Create button layout
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.setSpacing(5)
        # Create accept button
        btn_create_text = tr("CREATE CONFIGURATION") if not self.edit_mode else tr("SAVE CHANGES")
        self.btn_create = PrimaryPushButton(btn_create_text, self)
        self.btn_create.setMaximumWidth(600)
        self.btn_create.setEnabled(False) if self.edit_mode else None
        self.btn_create.clicked.connect(self.__handle_accept)
        btn_layout.addWidget(self.btn_create)
        # Create close button
        btn_close = PushButton(tr("CLOSE"), self)
        btn_close.setMaximumWidth(600)
        btn_layout.addWidget(btn_close)
        btn_close.clicked.connect(self.reject)

        return btn_layout

    def __handle_accept(self):
        """
        Validate input and emit the resulting payload data when the dialog is accepted.
        """
        data = self.__tabs.get_actual_data()
        if data is None:
            UiUtils.show_message(tr("Error"), tr("An error occurred while creating the data."), self)
            return
        if data["name"].strip() == "":
            UiUtils.show_message(tr("Error"), tr("The 'Name' field cannot be empty."), self)
            return
            
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, data["name"]):
            UiUtils.show_message(tr("Error"), tr("The name contains invalid characters for a folder."), self)
            return
            
        if not data["directories"] or len(data["directories"]) == 0:
            UiUtils.show_message(tr("Error"), tr("At least one folder must be associated with the configuration."), self)
            return
            
        self.signal_payload.emit(data, self.edit_mode)
        self.output_data = data
        self.accept()