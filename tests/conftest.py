import sys

import pytest

@pytest.fixture(scope="session")
def python_cmd():
    """Return path to the venv Python interpreter."""
    return f"{sys.prefix}/bin/python"