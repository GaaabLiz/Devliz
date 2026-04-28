# ==============================================================================
#
#    ____ _______ 
#   / __ \__   __|
#  | |  | | | |  
#  | |  | | | |  
#  | |__| | | |  
#   \___\_\ |_|  
#
#   _____ _    _ _____  _____   ____  ____  _____  _______
#  / ____| |  | |  __ \|  __ \ / __ \|  _ \|  __ \|__   __|
# | (___ | |  | | |__) | |__) | |  | | |_) | |__) |  | |
#  \___ \| |  | |  ___/|  ___/| |  | |  _ <|  _  /   | |
#  ____) | |__| | |    | |    | |__| | |_) | | \ \   | |
# |_____/ \____/|_|    |_|     \____/|____/|_|  \_\  |_|
#
#                    Qt / PySide6 OPTIONAL MODULE
#
#  This file adds Qt-specific make targets to your project.
#
#  HOW TO USE
#  ─────────────────────────────────────────────────────────────────────────────
#  1. Copy this file next to your Makefile (it should already be there).
#  2. Uncomment the following line inside project.mk:
#
#         include qt.mk
#
#  3. Override the variables below in project.mk BEFORE the include line,
#     or pass them on the command line:
#
#         make gen-qt-res-py QT_QRC_FILE=res/app.qrc
#
#  REQUIREMENTS
#  ─────────────────────────────────────────────────────────────────────────────
#  • PySide6 must be installed in the uv-managed virtual environment.
#  • The pyside6-rcc compiler is provided by the pyside6 package.
#
# ==============================================================================


# ==============================================================================
#  VARIABLES
#
#  All variables use ?= so they can be overridden from project.mk or the CLI.
# ==============================================================================

# The Qt resource compiler command.
# For PySide6 use pyside6-rcc; for PyQt6 use pyrcc6.
QT_COMMAND_GEN_RES ?= pyside6-rcc

# Source .qrc resource file to compile.
# Adjust this path to match your project layout.
QT_QRC_FILE ?= resources/resources.qrc

# Output path for the compiled Python resource module.
# This file is generated – do NOT edit it by hand and add it to .gitignore.
QT_RESOURCE_PY ?= $(PYTHON_MAIN_PACKAGE)/application/resources/resources_rc.py


# ==============================================================================
#  TARGETS
# ==============================================================================

## gen-qt-res-py        – Compile QT_QRC_FILE into a Python resource module
#
#  Runs the Qt resource compiler (pyside6-rcc / pyrcc6) to convert the .qrc
#  file into a Python module that can be imported at runtime.
#
#  Example:
#      make gen-qt-res-py
#      make gen-qt-res-py QT_QRC_FILE=res/icons.qrc QT_RESOURCE_PY=myapp/icons_rc.py
.PHONY: gen-qt-res-py
gen-qt-res-py:
	uv run $(QT_COMMAND_GEN_RES) $(QT_QRC_FILE) -o $(QT_RESOURCE_PY)
	@echo "Generated: $(QT_RESOURCE_PY)"
