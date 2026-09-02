from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget
from qfluentwidgets import (
    AdaptiveFlowLayout,
    BodyLabel,
    CaptionLabel,
    FluentIcon,
    IconWidget,
    PrimaryPushButton,
    SingleDirectionScrollArea,
    SimpleCardWidget,
    StrongBodyLabel,
)

from devliz.application.i18n import tr
from devliz.view.util.frame import DevlizQFrame


class HelpGuideCard(SimpleCardWidget):
    """
    Card widget representing a single help topic or guide.
    Clicking the card emits a signal to open detailed help.
    """

    signal_clicked = Signal(str)

    def __init__(self, card_id: str, icon: FluentIcon, title: str, subtitle: str, content: str, parent=None):
        """
        Initialize the help guide card.

        :param card_id: Unique identifier for the help topic.
        :param icon: FluentIcon to display on the card.
        :param title: Main title of the card.
        :param subtitle: Subtitle providing brief context.
        :param content: Summary text of the help topic.
        :param parent: Parent widget.
        """
        super().__init__(parent)
        self.card_id = card_id
        self.setMinimumHeight(220)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 16, 18, 16)
        root_layout.setSpacing(8)

        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(20, 20)

        title_label = StrongBodyLabel(title, self)
        subtitle_label = CaptionLabel(subtitle, self)
        subtitle_label.setWordWrap(True)
        subtitle_label.setTextColor("#707070", "#b0b0b0")

        content_label = BodyLabel(content, self)
        content_label.setWordWrap(True)

        root_layout.addWidget(icon_widget)
        root_layout.addWidget(title_label)
        root_layout.addWidget(subtitle_label)
        root_layout.addWidget(content_label)
        root_layout.addStretch(1)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events on the card to emit the clicked signal.

        :param event: The mouse event object.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.signal_clicked.emit(self.card_id)
        super().mousePressEvent(event)


class HelpDetailDialog(QDialog):
    """
    Dialog window for displaying detailed help information for a specific topic.
    """

    def __init__(self, title: str, subtitle: str, details: str, parent=None):
        """
        Initialize the detailed help dialog.

        :param title: The title of the help topic.
        :param subtitle: The subtitle of the help topic.
        :param details: The full detailed text of the help guide.
        :param parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(860, 620)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(12)

        title_label = StrongBodyLabel(title, self)
        subtitle_label = CaptionLabel(subtitle, self)
        subtitle_label.setWordWrap(True)
        subtitle_label.setTextColor("#606060", "#c5c5c5")

        scroll = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical, parent=self)
        scroll.setWidgetResizable(True)
        scroll.enableTransparentBackground()

        content_widget = QWidget(scroll)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(6, 6, 6, 6)

        details_label = BodyLabel(details, content_widget)
        details_label.setWordWrap(True)
        content_layout.addWidget(details_label)
        content_layout.addStretch(1)

        scroll.setWidget(content_widget)

        btn_close = PrimaryPushButton(tr("Close"), self)
        btn_close.clicked.connect(self.accept)

        root_layout.addWidget(title_label)
        root_layout.addWidget(subtitle_label)
        root_layout.addWidget(scroll, 1)
        root_layout.addWidget(btn_close)


class HelpView(DevlizQFrame):
    """
    Main view representing the Help module.
    Displays a grid of help guide cards that users can click to see details.
    """
    
    signal_card_clicked = Signal(str)

    def __init__(self, parent=None):
        """
        Initialize the HelpView.

        :param parent: Parent widget.
        """
        super().__init__(
            name=tr("Help"), 
            parent=parent, 
            subtitle=tr("A complete guide to every screen and workflow in Devliz.")
        )
        self.cards_layout = None
        self.cards_container = None
        self.__setup_ui()

    def __setup_ui(self):
        """
        Set up the UI layout.
        """
        self.install_label_title()

        scroll_layout = self.get_scroll_layout()

        self.cards_container = QWidget(self)
        self.cards_layout = AdaptiveFlowLayout(self.cards_container)
        self.cards_layout.setContentsMargins(4, 8, 4, 8)
        self.cards_layout.setHorizontalSpacing(12)
        self.cards_layout.setVerticalSpacing(12)
        self.cards_layout.setWidgetMinimumWidth(320)
        self.cards_layout.setWidgetMaximumWidth(560)

        scroll_layout.addWidget(self.cards_container)
        scroll_layout.addStretch(1)
        self.install_scroll_on(self.master_layout)

    def set_cards(self, cards):
        """
        Populate the UI layout with help guide cards.
        
        :param cards: List of card tuples.
        """
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        icon_map = {
            "info": FluentIcon.INFO,
            "home": FluentIcon.HOME,
            "book_shelf": FluentIcon.BOOK_SHELF,
            "search": FluentIcon.SEARCH,
            "setting": FluentIcon.SETTING,
            "history": FluentIcon.HISTORY,
            "save": FluentIcon.SAVE,
            "sync": FluentIcon.SYNC,
            "help": FluentIcon.HELP,
        }

        for card_id, icon_name, title, subtitle, content in cards:
            icon = icon_map.get(icon_name, FluentIcon.INFO)
            card = HelpGuideCard(card_id, icon, title, subtitle, content, self.cards_container)
            card.signal_clicked.connect(self.signal_card_clicked)
            self.cards_layout.addWidget(card)

    def show_details_dialog(self, title: str, subtitle: str, details: str):
        """
        Show the details dialog for the selected help card.

        :param title: The title of the help topic.
        :param subtitle: The subtitle of the help topic.
        :param details: The detailed text of the help topic.
        """
        dialog = HelpDetailDialog(title, subtitle, details, self)
        dialog.exec()
