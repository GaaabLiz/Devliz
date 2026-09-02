from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from pylizlib.core.data.gen import gen_random_string
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.widgets.input import MultiSelectionComboBox
from qfluentwidgets import BodyLabel, LineEdit, MessageBox

from devliz.application.app import snap_settings
from devliz.application.i18n import tr


class TabDetails(QWidget):
    """
    Widget containing the details form for a snapshot configuration.
    Allows editing properties like name, description, tags, and custom data.
    """

    signal_data_changed = Signal(bool)

    def __init__(
            self,
            payload_data: Snapshot | None = None,
            tags: list[str] = [],
            custom_data_keys: list[str] = [],
    ):
        """
        Initialize the TabDetails widget.

        :param payload_data: Existing snapshot data to populate the form with, if in edit mode.
        :param tags: Available tags for the snapshot.
        :param custom_data_keys: List of custom keys used to dynamically generate input fields.
        """
        super().__init__()
        self.payload_data: Snapshot | None = payload_data
        self.tags = tags
        self.layout = QVBoxLayout(self)
        self.custom_data_keys = custom_data_keys
        self.custom_data_inputs = {}

        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.setSpacing(20)

        # Create form fields
        self.__create_fields(self.tags)

        # Add to main layout
        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        # If in edit mode, populate the fields
        if self.payload_data:
            self.__populate_fields()
            self._capture_initial_state()
            self._connect_change_signals()


    def __create_fields(self, tags: list[str]):
        """
        Dynamically create UI fields for the form based on configuration.

        :param tags: A list of tags available for selection.
        """
        # ID Field
        self.form_id_label = BodyLabel(tr("ID:"), self)
        self.form_id_value = LineEdit()
        self.form_id_value.setText(gen_random_string(snap_settings.snap_id_length))
        self.form_id_value.setReadOnly(True)
        self.form_id_value.setMaximumWidth(500)
        self.form_layout.addRow(self.form_id_label, self.form_id_value)

        # Name Field
        self.form_name_label = BodyLabel(tr("Name:"), self)
        self.form_name_input = LineEdit()
        self.form_name_input.setMaximumWidth(500)
        self.form_layout.addRow(self.form_name_label, self.form_name_input)

        # Description Field
        self.form_desc_label = BodyLabel(tr("Description:"), self)
        self.form_desc_input = LineEdit()
        self.form_desc_input.setMaximumWidth(500)
        self.form_layout.addRow(self.form_desc_label, self.form_desc_input)

        # Tags Field
        self.form_tags_label = BodyLabel(tr("Tags:"), self)
        self.form_tags_input = MultiSelectionComboBox(self)
        self.form_tags_input.addItems(tags)
        self.form_tags_input.setMaximumWidth(500)
        self.form_tags_input.setPlaceholderText(tr("Add tag..."))
        self.form_layout.addRow(self.form_tags_label, self.form_tags_input)
        
        self.form_tags_input.installEventFilter(self)

        # Custom Fields
        for key in self.custom_data_keys:
            label = BodyLabel(f"{key.capitalize()}:", self)
            line_edit = LineEdit()
            line_edit.setMaximumWidth(500)
            self.form_layout.addRow(label, line_edit)
            self.custom_data_inputs[key] = line_edit
            
    def eventFilter(self, obj, event):
        """
        Event filter to handle specific UI events on widgets, like empty tags feedback.
        """
        if obj == self.form_tags_input and event.type() == QEvent.Type.MouseButtonPress:
            if not self.tags:
                w = MessageBox(tr("No tags"), tr("No tags found. Please create them in the Settings."), self)
                w.yesButton.hide()
                w.cancelButton.setText(tr("Close"))
                w.exec()
                return True
        return super().eventFilter(obj, event)

    def __populate_fields(self):
        """
        Populate the form fields using the provided payload data.
        """
        if not self.payload_data:
            return
        self.form_id_value.setText(self.payload_data.id)
        self.form_name_input.setText(self.payload_data.name)
        self.form_desc_input.setText(self.payload_data.desc)
        self.form_tags_input.setCheckedItems(self.payload_data.tags)
        if hasattr(self.payload_data, 'data') and self.payload_data.data:
            for key, widget in self.custom_data_inputs.items():
                widget.setText(self.payload_data.data.get(key, ""))

    def _capture_initial_state(self):
        """
        Capture the initial state of the form fields to determine if modifications occurred.
        """
        self._initial = {
            "name": self.form_name_input.text(),
            "desc": self.form_desc_input.text(),
            "tags": set(self.form_tags_input.get_items()),
            "custom_data": {
                key: widget.text() for key, widget in self.custom_data_inputs.items()
            }
        }

    def _connect_change_signals(self):
        """
        Connect value changed signals of inputs to trigger change evaluation.
        """
        self.form_name_input.textChanged.connect(self._on_changed)
        self.form_desc_input.textChanged.connect(self._on_changed)
        self.form_tags_input.selectionChanged.connect(lambda _: self._on_changed())
        for widget in self.custom_data_inputs.values():
            widget.textChanged.connect(self._on_changed)

    def _on_changed(self):
        """
        Evaluate if the current form state differs from the initial one and emit the signal_data_changed signal.
        """
        current = {
            "name": self.form_name_input.text(),
            "desc": self.form_desc_input.text(),
            "tags": set(self.form_tags_input.get_items()),
            "custom_data": {
                key: widget.text() for key, widget in self.custom_data_inputs.items()
            }
        }
        changed = (current != self._initial)
        self.signal_data_changed.emit(changed)

    def get_custom_data(self) -> dict[str, str]:
        """
        Return a dictionary with the custom data inputted into the form.

        :return: A dictionary mapping custom keys to their inputted string values.
        """
        return {key: widget.text() for key, widget in self.custom_data_inputs.items()}