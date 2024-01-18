from shlex import split
import subprocess


def run_command(cmd):
    """Run a command, and return the output."""
    cmd_parts = split(cmd)
    result = subprocess.run(cmd_parts,
        capture_output=True, text=True, check=True)
    
    return result.stdout.strip()
