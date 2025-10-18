from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from pylizlib.core.data.gen import gen_random_string
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.widgets.input import MultiSelectionComboBox
from qfluentwidgets import BodyLabel, LineEdit, ComboBox


class TabDetails(QWidget):

    signal_data_changed = Signal(bool)

    def __init__(
            self,
            payload_data: Snapshot | None = None,
            tags: list[str] = [],
    ):
        super().__init__()
        self.payload_data: Snapshot | None = payload_data
        self.tags = tags
        self.layout = QVBoxLayout(self)

        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.setSpacing(20)

        # Creo i campi
        self.__create_fields(self.tags)

        # Aggiungo tutto al layout principale
        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        # Se sono in edit mode, popolo i campi
        if self.payload_data:
            self.__populate_fields()
            self._capture_initial_state()
            self._connect_change_signals()


    def __create_fields(self, tags: list[str]):
        # Campo id
        self.form_id_label = BodyLabel("ID:", self)
        self.form_id_value = LineEdit()
        self.form_id_value.setText(gen_random_string(10))
        self.form_id_value.setReadOnly(True)
        self.form_id_value.setMaximumWidth(250)
        self.form_layout.addRow(self.form_id_label, self.form_id_value)

        # Campo nome
        self.form_name_label = BodyLabel("Nome:", self)
        self.form_name_input = LineEdit()
        self.form_name_input.setMaximumWidth(250)
        self.form_layout.addRow(self.form_name_label, self.form_name_input)

        # Campo descrizione
        self.form_desc_label = BodyLabel("Descrizione:", self)
        self.form_desc_input = LineEdit()
        self.form_desc_input.setMaximumWidth(250)
        self.form_layout.addRow(self.form_desc_label, self.form_desc_input)

        # Campo famiglia macchine
        self.form_family_label = BodyLabel("Famiglia macchine:", self)
        self.form_family_combo = ComboBox()
        items = ['UNKNOWN', "EASY", "FLEX", "SPEEDY"]
        self.form_family_combo.addItems(items)
        self.form_family_combo.setMaximumWidth(250)
        self.form_layout.addRow(self.form_family_label, self.form_family_combo)

        # Campo Modello
        self.form_model_label = BodyLabel("Modello:", self)
        self.form_model_input = LineEdit()
        self.form_model_input.setMaximumWidth(250)
        self.form_layout.addRow(self.form_model_label, self.form_model_input)

        # Campo tags
        self.form_tags_label = BodyLabel("Tags:", self)
        self.form_tags_input = MultiSelectionComboBox(self)
        self.form_tags_input.addItems(tags)
        self.form_tags_input.setMaximumWidth(250)
        self.form_tags_input.setPlaceholderText("Aggiungi tag...")
        self.form_layout.addRow(self.form_tags_label, self.form_tags_input)

    def __populate_fields(self):
        if not self.payload_data:
            return
        self.form_id_value.setText(self.payload_data.id)
        self.form_name_input.setText(self.payload_data.name)
        self.form_desc_input.setText(self.payload_data.desc)
        self.form_family_combo.setCurrentText(self.payload_data.machineFamily.value)
        self.form_model_input.setText(self.payload_data.machineModel)
        self.form_tags_input.setCheckedItems(self.payload_data.tags)

    def _capture_initial_state(self):
        self._initial = {
            "name": self.form_name_input.text(),
            "desc": self.form_desc_input.text(),
            "family": self.form_family_combo.currentText(),
            "model": self.form_model_input.text(),
            "tags": set(self.form_tags_input.get_items()),
        }

    def _connect_change_signals(self):
        self.form_name_input.textChanged.connect(self._on_changed)
        self.form_desc_input.textChanged.connect(self._on_changed)
        self.form_family_combo.currentTextChanged.connect(self._on_changed)
        self.form_model_input.textChanged.connect(self._on_changed)
        self.form_tags_input.selectionChanged.connect(lambda _: self._on_changed())

    def _on_changed(self):
        current = {
            "name": self.form_name_input.text(),
            "desc": self.form_desc_input.text(),
            "family": self.form_family_combo.currentText(),
            "model": self.form_model_input.text(),
            "tags": set(self.form_tags_input.get_items()),
        }
        changed = (current != self._initial)
        self.signal_data_changed.emit(changed)