## [0.2.0] - 2026-08-28

### 🚀 Features

- Implement HomeController and HomeView for displaying home statistics
- Translate UI strings to English using the i18n module for better localization support across the application. Updated various labels, messages, and dialog texts in the catalogue, dashboard, settings, and searcher views to enhance user experience for English-speaking users.
- Refactor CatalogueController to accept a search page opener and update CatalogueSearcherView to inherit from DevlizQFrame for improved UI integration
- Update DashboardController to manage UI states during data updates for home, catalogue, and searcher views
- Add HelpController and HelpView for user assistance and guidance in the application
- Implement ActionHistoryController and ActionHistoryView for managing and displaying user action history
- Add Italian translations for various UI strings to enhance localization support
- Integrate action logging across Catalogue, Search, Dashboard, Help, and Settings modules for enhanced user activity tracking
- Add unit tests for ActionHistory and Dashboard modules to improve code coverage and reliability
- *(backups)* Add backups section with management actions and settings
- *(ui)* Improve home dashboard cards and layout behavior
- *(ui)* Enhance home dashboard with additional snapshot statistics and improved card layout
- *(ui)* Update directory opening method to use QDesktopServices for better compatibility
- *(splash)* Implement splash screen controller with catalogue path validation
- *(i18n)* Add Italian translations for catalogue error messages and default options
- *(splash)* Refactor splash screen handling to use SplashController
- *(validation)* Implement NetworkFolderValidator to allow non-existent network paths for catalogue
- *(splash)* Add hide_overlay method and update splash screen handling
- *(settings)* Improve application restart handling and streamline directory opening
- *(i18n)* Add Italian translations for new tags and folder management messages
- *(catalogue)* Rename button text from "Add local folder" to "Add folder"
- *(catalogue)* Increase maximum width of input fields and add event filter for tag input
- *(catalogue)* Simplify import dialog text and validate folder name for invalid characters
- *(help)* Add Action History section with detailed descriptions for tracking application events
- *(backup)* Add FakeBackupController and related settings for backup functionality
- *(frame)* Replace IndeterminateProgressBar with ProgressBar and enhance updating functionality
- *(dashboard)* Enhance update process with progress and message signals
- *(dashboard)* Add progress and text signals for update feedback
- *(catalogue)* Implement heavy operation handling for snapshot modifications and installations
- Add subtitles to various views for enhanced context and usability
- *(action_history)* Introduce ActionCategory and ActionType enums for structured action logging
- *(backup)* Enhance action logging with ActionCategory and ActionType enums
- *(backup)* Update folder opening method to use QDesktopServices for better compatibility
- *(catalogue)* Refactor action logging to use ActionCategory and ActionType enums for improved structure
- *(catalogue_searcher)* Refactor action logging to use ActionCategory and ActionType enums; enhance folder opening method for better compatibility
- *(catalogue_searcher)* Enhance logging and introduce view switching functionality in search results
- Enhance logging. improve folder handling. Created enum class for action history handling

### 🐛 Bug Fixes

- *(dashboard)* Correct spacing in type hint for cached_data variable

### 💼 Other

- V0.2.0

### 🧪 Testing

- Add unit tests for various controllers and models

### ⚙️ Miscellaneous Tasks

- Update changelog [skip ci]
- Remove accidental temp request note file
- Add .vscode/ to .gitignore to exclude Visual Studio Code settings
- Updated some packages
- Update .gitignore to include temp directory
## [0.1.5] - 2026-04-28

### 🚀 Features

- Add setting to clear attached folders before snapshot installation
- Add Makefile and project.mk for build automation and project configuration
- Add CI workflows for quality checks and package publishing to Docker Hub and PyPI
- Add configuration files for Ruff and Ty to enhance linting and type checking
- Update dependencies in pyproject.toml for improved compatibility and features
- Add Makefile run configurations for various build and testing targets

### 💼 Other

- V0.1.5

### 🚜 Refactor

- Update JDK references in project configuration files for consistency

### ⚙️ Miscellaneous Tasks

- Add temporary logo assets in SVG, PNG, and ICO formats
- Update resource compiler version to Qt 6.11.0
## [0.1.4] - 2026-01-10

### 🚀 Features

- Add sorting functionality for snapshots
- Add sorting functionality to snapshot catalogue
- Add search actions for internal content in the command bar
- Implement UI builder for DevlizQFrame and refactor label installation
- Add catalogue search functionality with UI integration
- Add context menu for results table with delete action
- Add delete functionality for snapshots in catalogue searcher
- Enhance search results model with snapshot state and removal functionality
- Enhance snapshot search functionality with progress and status updates
- Add JSON file extension support and update task message handling
- Add task start handling and update status card message during search
- Add XML file extension support to the search functionality
- Add reset search state functionality to clear progress and status data
- Add search results tree model to display snapshot search results
- Add results count tracking and file opening functionality in searcher
- Add input validation for search text and update delete action label
- Update pylizlib version to 0.3.65 and update wheel URL
- Add functionality for single snapshot search and update loading behavior
- Add new catalogue.py file for improved catalog management
- Implement CatalogueModel and SnapshotTableModel for improved snapshot management
- Completely refactor controller/model/view classes of dashboard and catalogue
- Add delay between tasks in dashboard operation info for improved performance
- Add methods to count snapshots and calculate total size in SnapshotTableModel
- Add export and delete context menus for snapshots and installed folders
- Add export and delete functionality for snapshots and associated folders
- Add sorting option by associated directory size in snapshot menu
- Add functionality to open associated directories from snapshot context menu
- Enhance search functionality with query type and target selection inside catalogue_searcher.py
- Add detailed docstrings to CatalogueSearcher classes and methods for better clarity

### 🐛 Bug Fixes

- Remove duplicate import of os in catalogue.py
- Correct line continuation in makefile for resource generation command

### 💼 Other

- Upgrade pylizlib
- Bump version to 0.1.1
- Bump version to 0.1.2
- Bump version to 0.1.3
- Bump version to 0.1.4

### 🚜 Refactor

- Update path variable names for consistency
- Rename DevlizSettings to AppSettings for consistency
- Update log messages and titles for application consistency
- Streamline logging setup for improved readability
- Rename dash_controller.py and dash_model.py to dashboard.py and update imports
- Remove unnecessary delay parameter from OperationInfo in dashboard.py
- Rename catalogue_controller.py to catalogue.py and update import in dashboard.py
- Streamline action definitions in catalogue.py for improved readability
- Rename widget imports and streamline directory structure
- Rename catalogue searcher files for consistency and clarity

### 📚 Documentation

- Update changelog for 0.1.0

### ⚙️ Miscellaneous Tasks

- Moved workflow
- Update package versions for psutil, pylizlib, pyside6-fluent-widgets, and ruff
- Update pylizlib to version 0.3.63 and refresh package URLs
- Update pylizlib version to 0.3.67 and adjust package URLs
- Update Python SDK version in project configuration files
- Updated uv.lock
- Update resource compiler version in resources_rc.py to 6.10.1
## [0.1.0] - 2025-10-25

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
- Update build configuration and streamline release process
- Hide console window in Windows executable build
- Update project version to 0.1.0
- Refactor makefile and add project.mk for improved build management
- Update .gitignore to include Output directory
- Downgrade project version to 0.1.0 and add pyinstaller as a dependency
- Add Inno Setup script for PySide6 installer
- Integrate loguru-logging-intercept for enhanced logging management
- Add theme selection options to application settings
- Update release workflow to create Windows installer with Inno Setup

### 🐛 Bug Fixes

- Removed demo.py
- Reduce splash screen duration from 3 seconds to 1 second

### 💼 Other

- Updated deps versions
- Updated uv.lock
- Bump version to 0.1.1
- Bump version to 0.1.2
- Bump version to 0.1.3
- Downgrade version to 0.1.0
- Downgrade version to 0.1.0
- Downgrade version to 0.1.0

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

### 📚 Documentation

- Update changelog for 1.0.0
- Update changelog for 1.0.0
- Update changelog for 0.1.1
- Update changelog for 0.1.3

### ⚙️ Miscellaneous Tasks

- Update package versions for idna and pylizlib
- Add author information and update pylizlib version to 0.3.28
- Update dependencies in pyproject.toml and uv.lock for improved development support
- Update pylizlib version to 0.3.38 and adjust package metadata
