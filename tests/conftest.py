import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def python_cmd():
    """Return path to the venv Python interpreter."""
    if sys.platform == "win32":
        python_cmd = Path(sys.prefix) / "Scripts/python.exe"
    else:
        python_cmd = Path(sys.prefix) / "bin/python"

    return python_cmd.as_posix()
