from loguru import logger

from devliz.domain.data import DevlizSnapshotData
from devliz.view.home import HomeView


class HomeController:

    def __init__(self):
        self.view = HomeView()

    def update_data(self, snapshot_data: DevlizSnapshotData):
        logger.debug("Calcolo statistiche Home...")
        stats = snapshot_data.compute_home_statistics()
        logger.debug(f"Statistiche calcolate: {stats}")
        self.view.update_statistics(stats)
