from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QWidget
from qfluentwidgets import (
    SimpleCardWidget, SubtitleLabel, CaptionLabel, TitleLabel,
    setFont, FluentIcon, IconWidget, BodyLabel
)

from devliz.domain.data import HomeStatistics
from devliz.view.util.frame import DevlizQFrame
from devliz.application.i18n import tr


class StatCard(SimpleCardWidget):
    """Card che mostra una singola statistica con icona, titolo e valore."""

    def __init__(self, icon: FluentIcon, title: str, value: str = "—", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.setMinimumWidth(200)
        self.setBorderRadius(8)

        self.iconWidget = IconWidget(icon, self)
        self.iconWidget.setFixedSize(32, 32)

        self.titleLabel = CaptionLabel(title, self)
        self.titleLabel.setTextColor("#606060", "#d2d2d2")

        self.valueLabel = TitleLabel(value, self)
        setFont(self.valueLabel, 28)

        self.subtitleLabel = CaptionLabel(subtitle, self)
        self.subtitleLabel.setTextColor("#909090", "#a0a0a0")

        vLayout = QVBoxLayout(self)
        vLayout.setContentsMargins(20, 16, 20, 16)
        vLayout.setSpacing(4)

        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(10)
        headerLayout.addWidget(self.iconWidget)
        headerLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        headerLayout.addStretch(1)

        vLayout.addLayout(headerLayout)
        vLayout.addStretch(1)
        vLayout.addWidget(self.valueLabel)
        vLayout.addWidget(self.subtitleLabel)

    def update_value(self, value: str, subtitle: str = ""):
        self.valueLabel.setText(value)
        self.subtitleLabel.setText(subtitle)


class HomeView(DevlizQFrame):

    def __init__(self, parent=None):
        super().__init__(name=tr("Home"), parent=parent)
        self.__setup_ui()

    def __setup_ui(self):
        self.install_label_title()

        self.card_snap_count = StatCard(
            FluentIcon.PHOTO, tr("Snapshot Count"), parent=self
        )
        self.card_total_size = StatCard(
            FluentIcon.CLOUD, tr("Total Size"), parent=self
        )
        self.card_total_files = StatCard(
            FluentIcon.DOCUMENT, tr("Total Files"), parent=self
        )
        self.card_total_dirs = StatCard(
            FluentIcon.FOLDER, tr("Total Folders"), parent=self
        )
        self.card_heaviest_file = StatCard(
            FluentIcon.CALORIES, tr("Heaviest File"), parent=self
        )

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(16, 8, 16, 16)

        grid.addWidget(self.card_snap_count, 0, 0)
        grid.addWidget(self.card_total_size, 0, 1)
        grid.addWidget(self.card_total_files, 0, 2)
        grid.addWidget(self.card_total_dirs, 1, 0)
        grid.addWidget(self.card_heaviest_file, 1, 1, 1, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        self.master_layout.addLayout(grid)
        self.master_layout.addStretch(1)

    def update_statistics(self, stats: HomeStatistics):
        self.card_snap_count.update_value(str(stats.snapshot_count))
        self.card_total_size.update_value(stats.total_size_str)
        self.card_total_files.update_value(f"{stats.total_files:,}".replace(",", "."))
        self.card_total_dirs.update_value(f"{stats.total_dirs:,}".replace(",", "."))

        if stats.heaviest_file_path:
            from pathlib import Path
            name = Path(stats.heaviest_file_path).name
            self.card_heaviest_file.update_value(
                stats.heaviest_file_size_str,
                subtitle=name
            )
        else:
            self.card_heaviest_file.update_value("—", subtitle=tr("No file found"))
