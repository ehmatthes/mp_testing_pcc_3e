import sys
from pathlib import Path

import pytest

import utils


# --- CLI args ---

def pytest_addoption(parser):
    parser.addoption(
        "--pygame-version", action="store",
        default=None,
        help="Pygame version to test"
    )


# --- Fixtures ---

@pytest.fixture(scope="session")
def python_cmd():
    """Return path to the venv Python interpreter."""
    return utils.get_python_cmd()


# --- Cleanup ---

def pytest_sessionfinish(session, exitstatus):
    """Custom cleanup work."""

    # Show which version of Python was used for tests.
    python_cmd = utils.get_python_cmd()
    cmd = f"{python_cmd} --version"
    output = utils.run_command(cmd)

    print(f"\n***** Tests were run with: {output}")
