import subprocess, sys, re
from shlex import split
from pathlib import Path


def run_command(cmd):
    """Run a command, and return the output."""
    cmd_parts = split(cmd)
    result = subprocess.run(cmd_parts,
        capture_output=True, text=True, check=True,
        encoding="utf-8")
    
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
    cmd = f"{python_cmd} -m pip freeze"
    output = run_command(cmd)
    lib_output = [
        line for line in output.splitlines()
        if lib_name in line
    ]

    print(f"\n*** Running tests with {lib_output}\n")


def add_plotly_write_commands(path, lines):
    """Add commands to write HTML file, with and without plotly.js.
    I want the usual version with plotly.js, for viewing.
    But testing against a reference file is more reliable
      without including plotly.js.
    """
    # Add call to fig.write_html()
    output_filename = path.name.replace(".py", ".html")
    save_cmd = f'fig.write_html("{output_filename}")'
    lines.append(save_cmd)

    # Add call to fig.write_html(), without inline plotly.js.
    output_filename_nojs = output_filename.replace(
        ".html", "_nojs.html")
    save_cmd_nojs = f'\nfig.write_html("{output_filename_nojs}", include_plotlyjs=False)'
    lines.append(save_cmd_nojs)

    return lines


def replace_plotly_hash(path):
    """Replace Plotly's unique hash ID with "dummy-id"."""
    contents = path.read_text()
    hash_id = re.search(r'div id="([a-f0-9\-]{36})"',
            contents).group(1)
    contents = contents.replace(hash_id, "dummy-id")
    path.write_text(contents)