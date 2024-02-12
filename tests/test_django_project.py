import os, shutil
from pathlib import Path

import utils

def test_django_project(tmp_path, python_cmd):
    """Test the Learning Log project."""

    # Copy project to temp dir.
    src_dir = (Path(__file__).parents[1] / "chapter_20"
            / "deploying_learning_log")
    dest_dir = tmp_path / "learning_log"
    shutil.copytree(src_dir, dest_dir)

    # All remaining work needs to be done in dest_dir.
    os.chdir(dest_dir)

    # Build a fresh venv for the project.
    cmd = f"{python_cmd} -m venv ll_env"
    output = utils.run_command(cmd)
    assert output == ""

    # Get python command from ll_env.
    llenv_python_cmd = (dest_dir
            / "ll_env" / "bin" / "python")

    # Run `pip freeze` to prove we're in a fresh venv.
    cmd = f"{llenv_python_cmd} -m pip freeze"
    output = utils.run_command(cmd)
    assert output == ""