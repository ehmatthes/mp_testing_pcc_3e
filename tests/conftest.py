import sys
from pathlib import Path

import pytest

import utils


@pytest.fixture(scope="session")
def python_cmd():
    """Return path to the venv Python interpreter."""
    return utils.get_python_cmd()


