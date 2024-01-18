import subprocess, sys
from pathlib import Path
from shlex import split
import sys

def test_basic_program():
    """Test a program that only prints output."""
    root_dir = Path(__file__).parents[1]
    path = root_dir / "chapter_01" / "hello_world.py"

    # Use the venv python.
    python_cmd = f"{sys.prefix}/bin/python"
    cmd = f"{python_cmd} {path}"

    # Run the command, and make assertions.
    cmd_parts = split(cmd)
    result = subprocess.run(cmd_parts,
        capture_output=True, text=True, check=True)
    output = result.stdout.strip()

    assert output == "Hello Python world!"