import importlib
import sys

import pytest


@pytest.fixture
def fresh_import():
    """Importa un modulo forzando reload e cache pulita."""

    def _import(module_name: str):
        sys.modules.pop(module_name, None)
        return importlib.import_module(module_name)

    return _import

