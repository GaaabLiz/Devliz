from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import SubtitleLabel, setFont, SingleDirectionScrollArea, ProgressBar, BodyLabel, CaptionLabel

from devliz.application.i18n import tr



class DevlizQFrameUiBuilder:
    """
    Builder class for creating UI components used within DevlizQFrame.
    """

    def __init__(self, parent=None):
        """
        Initialize the UI builder.

        :param parent: The parent widget for the created UI components.
        """
        self.parent = parent

    def get_updating_progress_bar(self):
        """
        Create and configure a progress bar for the updating state.

        :return: A customized ProgressBar instance.
        """
        progress_bar = ProgressBar(self.parent)
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        return progress_bar

    def get_label_updating(self):
        """
        Create a label to show the 'Updating' status message.

        :return: A BodyLabel instance with the updating text.
        """
        updating_label = BodyLabel(tr("Updating, please wait"), parent=self.parent)
        updating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return updating_label

    def get_label_updating_details(self):
        """
        Create a label for showing specific details during the update process.

        :return: A CaptionLabel instance for update details.
        """
        label = CaptionLabel("", parent=self.parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def get_label_title(self, text) -> SubtitleLabel:
        """
        Create a customized title label.

        :param text: The text to display in the title label.
        :return: A formatted SubtitleLabel instance.
        """
        label = SubtitleLabel(text, self.parent)
        setFont(label, 24)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label


class DevlizQFrame(QFrame):
    """
    Base frame widget for Devliz views, providing standard layout, scrolling, and update state handling.
    """

    def __init__(self, name: str, parent=None, subtitle: str = ""):
        """
        Initialize the DevlizQFrame.

        :param name: The name of the window/view (used for title and object name).
        :param parent: The parent widget.
        :param subtitle: Optional subtitle displayed below the title.
        """
        super().__init__(parent=parent)
        self.setObjectName(name.replace(' ', '-'))
        self.window_name = name
        self.window_subtitle = subtitle
        self.__builder = DevlizQFrameUiBuilder(self)

        # --- Layout per il widget di aggiornamento
        self._top_level_layout = QVBoxLayout(self)
        self._top_level_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._top_level_layout.setContentsMargins(0, 0, 0, 0)

        # --- Widget di aggiornamento ---
        self.__updating_widget = QWidget(self)
        updating_layout = QVBoxLayout(self.__updating_widget)
        updating_layout.setContentsMargins(0, 0, 0, 0)
        
        self.__det_prog_bar = self.__builder.get_updating_progress_bar()
        self.__upd_label = self.__builder.get_label_updating()
        self.__upd_detail_label = self.__builder.get_label_updating_details()
        
        updating_layout.addWidget(self.__det_prog_bar)
        updating_layout.addStretch()
        updating_layout.addWidget(self.__upd_label)
        updating_layout.addWidget(self.__upd_detail_label)
        updating_layout.addStretch()
        self._top_level_layout.addWidget(self.__updating_widget)

        # --- Main Content Widget ---
        self.__main_content_widget = QWidget(self)
        self._top_level_layout.addWidget(self.__main_content_widget)

        self.master_layout = QVBoxLayout(self.__main_content_widget)
        self.master_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        self.__scroll_area = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_view = QWidget()
        self.scroll_layout = QVBoxLayout(self.__scroll_view)

        self.set_state(UiWidgetMode.DISPLAYING)


    def get_scroll_layout(self) -> QVBoxLayout:
        """
        Get the layout assigned to the scroll area content widget.

        :return: The QVBoxLayout for the scroll view.
        """
        return self.scroll_layout

    def install_scroll_on(self, layout: QVBoxLayout):
        """
        Install the scroll area onto the specified layout.

        :param layout: The layout where the scroll area will be added.
        """
        self.__scroll_area.setWidget(self.__scroll_view)
        self.__scroll_area.enableTransparentBackground()
        layout.addWidget(self.__scroll_area)

    def set_state(self, mode: UiWidgetMode):
        """
        Switch the view state between displaying content and showing the updating progress.

        :param mode: The UI mode to set (DISPLAYING or UPDATING).
        """
        if mode == UiWidgetMode.UPDATING:
            self.__updating_widget.show()
            self.__main_content_widget.hide()
        elif mode == UiWidgetMode.DISPLAYING:
            self.__updating_widget.hide()
            self.__main_content_widget.show()

    def install_label_title(self):
        """
        Install the main title and optional subtitle labels in the master layout.
        """
        title_label = self.__builder.get_label_title(self.window_name)
        self.master_layout.addWidget(title_label)
        
        if self.window_subtitle:
            subtitle_label = CaptionLabel(self.window_subtitle, self)
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle_label.setWordWrap(True)
            subtitle_label.setTextColor("#606060", "#c5c5c5")
            self.master_layout.addWidget(subtitle_label)
        
    def set_updating_progress(self, progress: int):
        """
        Update the progress bar value.

        :param progress: The progress percentage (0-100).
        """
        self.__det_prog_bar.setValue(progress)
        
    def set_updating_text(self, text: str):
        """
        Update the main text shown during the updating state.

        :param text: The text to display.
        """
        self.__upd_label.setText(text)

    def set_updating_detail_text(self, text: str):
        """
        Update the detailed text shown during the updating state.

        :param text: The detailed text to display.
        """
        self.__upd_detail_label.setText(text)
