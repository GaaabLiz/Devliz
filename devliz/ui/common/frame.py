from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout
from qfluentwidgets import SubtitleLabel, setFont, SingleDirectionScrollArea


class DevlizQFrame(QFrame):

    def __init__(self, name: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(name.replace(' ', '-'))
        self.window_name = name

        self.__qframe_label = SubtitleLabel(name, self)
        setFont(self.__qframe_label, 24)
        self.__qframe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__scroll_area = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_view = QWidget()
        self.scroll_layout = QVBoxLayout(self.__scroll_view)

    def get_label_title(self) -> SubtitleLabel:
        return self.__qframe_label

    def get_scroll_layout(self) -> QVBoxLayout:
        return self.scroll_layout

    def install_scroll_on(self, layout: QVBoxLayout):
        self.__scroll_area.setWidget(self.__scroll_view)
        self.__scroll_area.enableTransparentBackground()
        layout.addWidget(self.__scroll_area)

