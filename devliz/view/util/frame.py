from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import SubtitleLabel, setFont, SingleDirectionScrollArea, IndeterminateProgressBar, BodyLabel


# noinspection PyMethodMayBeStatic
class DevlizQFrame(QFrame):

    def __init__(self, name: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(name.replace(' ', '-'))
        self.window_name = name

        # --- Layout per il widget di aggiornamento
        self._top_level_layout = QVBoxLayout(self)
        self._top_level_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._top_level_layout.setContentsMargins(0, 0, 0, 0)

        # --- Widget di aggiornamento ---
        self.__updating_widget = QWidget(self)
        updating_layout = QVBoxLayout(self.__updating_widget)
        updating_layout.setContentsMargins(0, 0, 0, 0)
        updating_layout.addWidget(self.__get_updating_progress_bar())
        updating_layout.addStretch()
        updating_layout.addWidget(self.__get_label_updating())
        updating_layout.addStretch()
        self._top_level_layout.addWidget(self.__updating_widget)

        # --- Main Content Widget ---
        self.__main_content_widget = QWidget(self)
        self._top_level_layout.addWidget(self.__main_content_widget)

        self.master_layout = QVBoxLayout(self.__main_content_widget)
        self.master_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.__qframe_label = SubtitleLabel(name, self)
        setFont(self.__qframe_label, 24)
        self.__qframe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__scroll_area = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_view = QWidget()
        self.scroll_layout = QVBoxLayout(self.__scroll_view)

        self.set_state(UiWidgetMode.DISPLAYING)


    def __get_updating_progress_bar(self):
        progress_bar = IndeterminateProgressBar(start=True)
        progress_bar.setRange(0, 0)  # Indeterminate
        return progress_bar

    def __get_label_updating(self):
        updating_label = BodyLabel("Aggiornamento in corso attendere", self)
        updating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return updating_label

    def get_label_title(self) -> SubtitleLabel:
        return self.__qframe_label

    def get_scroll_layout(self) -> QVBoxLayout:
        return self.scroll_layout

    def install_scroll_on(self, layout: QVBoxLayout):
        self.__scroll_area.setWidget(self.__scroll_view)
        self.__scroll_area.enableTransparentBackground()
        layout.addWidget(self.__scroll_area)

    def set_state(self, mode: UiWidgetMode):
        if mode == UiWidgetMode.UPDATING:
            self.__updating_widget.show()
            self.__main_content_widget.hide()
        elif mode == UiWidgetMode.DISPLAYING:
            self.__updating_widget.hide()
            self.__main_content_widget.show()
