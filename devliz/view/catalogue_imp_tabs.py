import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from loguru import logger
from pylizlib.core.data.gen import gen_random_string
from pylizlib.core.os.snap import Snapshot, SnapDirAssociation
from pylizlib.core.os.snap.domain import SnapshotSettings
from pylizlib.core.os.utils import get_system_username
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import SegmentedWidget

from devliz.application.app import app_settings, AppSettings
from devliz.domain.data import DevlizData
from devliz.view.catalogue_imp_tab_details import TabDetails
from devliz.view.catalogue_imp_tab_directories import TabDirectories
from devliz.application.i18n import tr


class DialogConfigTabs(QWidget):

    def __init__(
            self,
            devliz_data: DevlizData,
            payload_data: Snapshot | None = None,
    ):
        super().__init__()
        self.payload_data: Snapshot | None = payload_data

        # struttura principale
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        # Creo i tabs
        self.tab_details = TabDetails(self.payload_data, app_settings.get(AppSettings.config_tags), app_settings.get(AppSettings.snap_custom_data))
        self.tab_directories = TabDirectories(self.payload_data, app_settings.get(AppSettings.starred_dirs))

        # Aggiungo i tabs al pivot
        self.__add_sub_interface(self.tab_details, "details", tr("Details"))
        self.__add_sub_interface(self.tab_directories, "directories", tr("Folders"))

        # Aggiungo tutto al layout principale
        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        # Impostazioni globali del pivot
        self.stackedWidget.setCurrentWidget(self.tab_details)
        self.pivot.setCurrentItem(self.tab_details.objectName())
        self.pivot.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def __add_sub_interface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def get_actual_data(self) -> Snapshot | None:
        try:
            settings = SnapshotSettings()

            assoc: list[SnapDirAssociation] = []
            
            # Map existing paths to their associations if in edit mode
            existing_assocs = {a.original_path: a for a in self.payload_data.directories} if self.payload_data else {}

            index = 0
            for directory in self.tab_directories.directories:
                path_str = directory.__str__()
                if path_str in existing_assocs:
                    # Reuse existing association but update its index
                    old_a = existing_assocs[path_str]
                    assoc.append(
                        SnapDirAssociation(
                            original_path=old_a.original_path,
                            folder_id=old_a.folder_id,
                            index=index,
                            mb_size=old_a.mb_size
                        )
                    )
                else:
                    # Create new association
                    assoc.append(
                        SnapDirAssociation(
                            original_path=path_str,
                            folder_id=gen_random_string(settings.folder_id_length),
                            index=index
                        )
                    )
                index += 1

            if self.payload_data:
                data = self.payload_data.clone()
                data.name = self.tab_details.form_name_input.text()
                data.desc = self.tab_details.form_desc_input.text()
                data.tags = self.tab_details.form_tags_input.get_items()
                data.directories = assoc
                data.data = self.tab_details.get_custom_data()
            else:
                data = Snapshot(
                    id=self.tab_details.form_id_value.text(),
                    name=self.tab_details.form_name_input.text(),
                    desc=self.tab_details.form_desc_input.text(),
                    tags=self.tab_details.form_tags_input.get_items(),
                    date_created=datetime.datetime.now(),
                    author=get_system_username(),
                    directories=assoc,
                    data=self.tab_details.get_custom_data()
                )
            return data
        except Exception as e:
            logger.error(e)
            UiUtils.show_message(tr("Error"), tr("An error occurred while collecting the data."), self)
