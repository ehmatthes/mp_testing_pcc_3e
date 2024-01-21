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

def check_library_version(request, python_cmd, lib_name):
    """Install a specific version of a library if needed."""
    lib_version = request.config.getoption(f"--{lib_name}-version")

    if lib_version:
        print(f"\n*** Installing {lib_name} {lib_version}\n")
        cmd = f"{python_cmd} -m pip install {lib_name}=={lib_version}"
        output = run_command(cmd)
        print(output)

    # Regardless of what version was requested,
    # show which version is being used.
    cmd = f"{python_cmd} -m pip freeze | grep {lib_name}"
    result = subprocess.run(cmd, capture_output=True,
            text=True, check=True, shell=True)
    output = result.stdout.strip()

    print(f"\n*** Running tests with {output}\n")