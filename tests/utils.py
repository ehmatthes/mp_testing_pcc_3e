import subprocess, sys
from shlex import split
from pathlib import Path


def run_command(cmd):
    """Run a command, and return the output."""
    cmd_parts = split(cmd)
    result = subprocess.run(cmd_parts,
        capture_output=True, text=True, check=True)
    
    return result.stdout.strip()

def get_python_cmd():
    """Return path to the venv Python interpreter."""
    if sys.platform == "win32":
        python_cmd = Path(sys.prefix) / "Scripts/python.exe"
    else:
        python_cmd = Path(sys.prefix) / "bin/python"

    return python_cmd.as_posix()