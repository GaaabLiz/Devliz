## [1.0.0] - 2025-10-20

### 🚀 Features

- Added resources file
- Implement Devliz application settings and configuration
- Add DevlizSnapshotData and DevlizData classes for configuration management
- Add resource file in .py
- Add WidgetDemo class for displaying labeled widgets
- Create project.py for project metadata and dependencies
- Add makefile for project build and management
- Update dependencies in pyproject.toml for enhanced functionality
- Add main application entry point with dashboard controller
- Implement dashboard controller, model, and view for DevLiz application
- Remove commented-out custom scripts configuration from app.py
- Add splash screen implementation and update main application entry point
- Update dashboard view to use settings widget and change window title
- Add new modules for dialog and tab details functionality
- Add DevlizQFrame class for enhanced UI frame functionality
- Implement WidgetSettingsScrollable class for managing settings UI
- Implement WidgetSettingsScrollable class for managing settings UI
- Add CommitMessageInspectionProfile for enforcing commit message standards
- Introduce SettingGroupManager for improved settings UI management
- Implement SnapshotCatalogueWidget for managing snapshot configurations
- Add support for custom snapshot data in configuration settings
- Add TaskGetSnapshots class for retrieving saved snapshots
- Implement data update handling and signal emissions in dashboard components
- Add configuration import dialog with data validation and signal handling
- Refactor settings management to use QtFwQConfigItem for improved configuration handling
- Add configuration tabs for details and directories management in import dialog
- Enhance CatalogueController with configuration dialog handling and signal integration
- Add TaskGetSettingsData for configuration data retrieval
- Integrate TaskGetSettingsData into dashboard update process
- Refactor CatalogueController to use a callable for cached data retrieval
- Update TaskGetSnapshots to utilize SnapshotCatalogue for data retrieval
- Enhance catalogue components with custom data handling and integration
- Add custom snapshot data retrieval to devliz_update
- Add custom snapshot data retrieval to devliz_update
- Refactor dash_controller to streamline data update handling
- Enhance filtering logic in catalogue to include custom data values
- Implement snapshot management actions in catalogue controller
- Update snapshot management actions to include data updates after modifications
- Update pylizlib version to 0.3.43 and adjust package URLs
- Enhance snapshot catalogue initialization with backup path and options
- Update pylizlib version to 0.3.46 and adjust package URLs
- Increase snapshot ID size and update related data handling in TabDetails
- Add backup options for editing and deleting configurations
- Refactor logo resource handling to use a constant for window icons
- Implement directory opening for snapshots with existence check
- Update pylizlib version to 0.3.47 and adjust package URLs
- Add application settings group with options to open working folder and clear backups
- Refactor settings widget to use a simplified class structure
- Update pylizlib version to 0.3.48 and adjust package URLs
- Implement settings controller for managing catalogue path and backups
- Update psutil to version 7.1.1 and pylizlib to version 0.3.49
- Enhance logging in dashboard controller and model, remove unused settings task
- Simplify size calculation by using get_normalized_gb_mb_str and clean up unused DevlizSettingsData class
- Refactor catalogue import tabs to use app settings and remove unused settings data class
- Add snapshot settings configuration for backup management
- Implement backup directory management and enhance settings functionality
- Update package versions for pylizlib and typer
- Update ID generation to use snapshot settings for length configuration
- Integrate snapshot settings into SnapshotCatalogue initialization
- Bump version to 1.0.0
- Enable snapshots custom data option by default
- Add GitHub Actions workflow for automated build and release process

### 🐛 Bug Fixes

- Removed demo.py
- Reduce splash screen duration from 3 seconds to 1 second

### 💼 Other

- Updated deps versions
- Updated uv.lock

### 🚜 Refactor

- Update data generation method in dashboard controller
- Update data generation method in dashboard controller
- Rename catalogue files for improved clarity and organization
- Update import paths in dash_controller.py for improved module structure
- Rename module files for improved organization
- Rename and reorganize UI module files for improved structure
- Update import paths in main.py for improved module structure
- Update import path for resources in splash.py for improved module structure
- Rename resource module files for improved organization
- Update application initialization to include author information
- Enhance application window title by integrating app name from app module
- Rename setting_widget.py to setting.py for improved clarity
- Improve DashboardModel to support progress updates during data refresh
- Clean up imports in dash_model.py for improved readability
- Rename catalogue_dialog.py to catalogue_controller.py and integrate CatalogueController into the dashboard
- Remove redundant log message after data update in dash_controller.py
- Rename DevlizData to DevlizSettingsData and restructure data classes for better organization
- Enhance DashboardModel and introduce TaskGetMonitoredSoftware for improved data handling. started update logic
- Simplify TaskGetMonitoredSoftware initialization and remove unused progress calculation
- Streamline DashboardModel initialization and enhance operation handling
- Clean up whitespace in dash_view.py for improved readability
- Remove unused imports in dash_controller.py, dash_model.py, devliz_update.py, and splash.py for cleaner code
- Update resource path in makefile for correct resource file location
- Update resource import in dash_view.py and modify resource data in resources_rc.py
- Update pylizlib version to 0.3.36 and adjust associated URLs in uv.lock
- Consolidate OperationRunner initialization in dash_model.py for improved clarity
- Integrate logging functionality in app.py for enhanced debugging and monitoring
- Change logging level to debug for dashboard update events in dash_model.py
- Enhance DevlizQFrame with updating widget and progress bar for better user feedback
- Enhance settings management with new snapshot and favorites groups
- Add null check for signal before connecting widget click event
- Update dashboard state management during operation events
- Update pylizlib version to 0.3.37 and adjust sdist and wheels URLs
- Add MasterListSettingCard for custom snapshot data management
- Integrate SnapshotCatalogueWidget into dashboard interface
- Update dashboard state management on runner completion
- Simplify label creation in frame.py by moving it to get_label_title method
- Rename configurations to snapshots in DevlizSnapshotData for clarity
- Update update_widget method to use snapshot_data for clarity

### ⚙️ Miscellaneous Tasks

- Update package versions for idna and pylizlib
- Add author information and update pylizlib version to 0.3.28
- Update dependencies in pyproject.toml and uv.lock for improved development support
- Update pylizlib version to 0.3.38 and adjust package metadata
