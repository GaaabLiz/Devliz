import importlib
import os
import shutil
import sys
import tempfile

import pytest

temp_home = None

def pytest_configure(config):
    global temp_home
    temp_home = tempfile.mkdtemp(prefix="devliz_test_home_")
    os.environ["HOME"] = temp_home
    os.environ["USERPROFILE"] = temp_home
    os.environ["APPDATA"] = temp_home
    os.environ["LOCALAPPDATA"] = temp_home
    print(f"\n[Pytest] Set fake HOME to: {temp_home}")

def pytest_unconfigure(config):
    global temp_home
    if temp_home and os.path.exists(temp_home):
        shutil.rmtree(temp_home, ignore_errors=True)

@pytest.fixture
def fresh_import():
    """Importa un modulo forzando reload e cache pulita."""

    def _import(module_name: str):
        sys.modules.pop(module_name, None)
        return importlib.import_module(module_name)

    return _import
