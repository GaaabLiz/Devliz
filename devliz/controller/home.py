from devliz.domain.data import DevlizSnapshotData
from devliz.model.home import HomeModel
from devliz.view.home import HomeView


class HomeController:
    """
    Controller for the application's home screen.

    This class orchestrates the HomeModel and HomeView, connecting
    their signals and methods to maintain the MVC architecture.
    """

    def __init__(self):
        """
        Initializes the HomeController.

        Creates the associated HomeModel and HomeView instances, 
        and sets up the signal-slot connections between them.
        """
        self.model = HomeModel()
        self.view = HomeView()
        
        # MVC: Connect model signals to view slots
        self.model.statistics_updated.connect(self.view.update_statistics)

    def update_data(self, snapshot_data: DevlizSnapshotData):
        """
        Updates the data presented on the home view by commanding the model
        to re-compute statistics based on the latest snapshot data.

        Args:
            snapshot_data (DevlizSnapshotData): The current snapshot data used to compute statistics.
        """
        # Tell the model to compute new data. 
        # When it finishes, it will emit 'statistics_updated' triggering the view automatically.
        self.model.compute_and_emit_statistics(snapshot_data)
