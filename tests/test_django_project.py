"""Test the Learning Log project.

- Copy project to tmp dir.
- Build a venv there.
- Install [specified] version of Django there.
- Run migrations.
- Start runserver.
- Run functionality tests.
"""

import os
import platform
import shutil
import signal
import subprocess
from pathlib import Path
from time import sleep

import psutil
import requests

import utils
from resources.ll_e2e_tests import run_e2e_test
from resources.migration_output import migration_output


def test_django_project(request, tmp_path, python_cmd):
    """Test the Learning Log project."""

    # Copy project to temp dir.
    dest_dir = tmp_path / "learning_log"
    copy_to_temp_dir(dest_dir)

    # All remaining work needs to be done in dest_dir.
    os.chdir(dest_dir)

    # Process --django-version CLI arg.
    modify_requirements(request, dest_dir)

    # Build a fresh venv for the project.
    llenv_python_cmd = build_venv(python_cmd, dest_dir)

    migrate_project(llenv_python_cmd)
    check_project(llenv_python_cmd)

    run_e2e_tests(dest_dir, llenv_python_cmd)

    # Show what versions of Python and Django were used.
    show_versions(llenv_python_cmd)


# --- Helper functions ---

def copy_to_temp_dir(dest_dir):
    # Copy project to temp dir.
    src_dir = (Path(__file__).parents[1] / "chapter_20"
            / "deploying_learning_log")
    shutil.copytree(src_dir, dest_dir)


def modify_requirements(request, dest_dir):
    """Modify requirements.txt based on --django-version."""

    # Unpin requirements if appropriate.
    django_version = request.config.getoption("--django-version")

    if django_version is None:
        return

    # --django-version is "unpinned" or a specific version.
    #   Unpin requirements for both of these cases.
    print("\n***** Unpinning versions from requirements.txt")
    req_path = dest_dir / "requirements.txt"
    contents = "Django\ndjango-bootstrap5\nplatformshconfig\n"

    # If --django-version is not unpinned, then it's a 
    #   specific version that we need to set.
    if django_version != "unpinned":
        django_req = f"Django=={django_version}"
        contents = contents.replace("Django", django_req)

    req_path.write_text(contents)


def build_venv(python_cmd, dest_dir):
    """Build a venv just for this test run."""
    print("\n***** Building venv for test...")
    cmd = f"{python_cmd} -m venv ll_env"
    output = utils.run_command(cmd)
    assert output == ""

    # Get python command from ll_env.
    llenv_python_cmd = (dest_dir
            / "ll_env" / "bin" / "python")
    if platform.system() == "Windows":
        llenv_python_cmd = (dest_dir / "ll_env"
            / "Scripts" / "python.exe").as_posix()

    # Run `pip freeze` to prove we're in a fresh venv.
    cmd = f"{llenv_python_cmd} -m pip freeze"
    output = utils.run_command(cmd)
    assert output == ""

    # Install requirements, and requests for testing.
    cmd = f"{llenv_python_cmd} -m pip install -r requirements.txt"
    output = utils.run_command(cmd)
    cmd = f"{llenv_python_cmd} -m pip install requests"
    output = utils.run_command(cmd)

    # Run `pip freeze` again, verify installations.
    cmd = f"{llenv_python_cmd} -m pip freeze"
    output = utils.run_command(cmd)
    assert "Django==" in output
    assert "django-bootstrap5==" in output
    assert "platformshconfig==" in output
    assert "requests==" in output

    return llenv_python_cmd


def migrate_project(llenv_python_cmd):
    cmd = f"{llenv_python_cmd} manage.py migrate"
    output = utils.run_command(cmd)
    assert migration_output in output


def check_project(llenv_python_cmd):
    cmd = f"{llenv_python_cmd} manage.py check"
    output = utils.run_command(cmd)
    assert "System check identified no issues (0 silenced)." in output


def run_e2e_tests(dest_dir, llenv_python_cmd):
    """Run e2e tests against the running project.
    This has to start a dev server, keep it running through
      the e2e tests, then shut down the server. This needs
      to work on macOS and Windows.
    """
    print("***** Running e2e tests...")
    # Log to file, so we can verify we haven't connected to a
    #   previous server process, or an unrelated one.
    log_path = dest_dir / "runserver_log.txt"
    server_process = start_server(llenv_python_cmd, log_path)
    check_server_ready(log_path)

    # If e2e test is not run in a try block, a failed assertion will
    #   prevent the server from being terminated correctly.
    try:
        run_e2e_test("http://localhost:8008/")
    except AssertionError as e:
        raise e
    finally:
        stop_server(server_process)


def start_server(llenv_python_cmd, log_path):
    """Start the dev server for e2e tests."""
    print("***** Starting server...")
    # Start development server.
    #   To verify it's not running after the test:
    #   macOS: `$ ps aux | grep runserver`
    #   Windows: Resource Monitor > python.exe
    #      Associated Handles > runserver
    #      > tasklist | findstr "python"
    #      > taskkill /F /PID <pid>
    # I may have other projects running on 8000; run this on 8008.
    #   shell=True is necessary for redirecting output.
    #   start_new_session=True is required to terminate the process group.
    cmd = f"{llenv_python_cmd} manage.py runserver 8008"
    cmd += f" > {log_path} 2>&1"
    server_process = subprocess.Popen(cmd, shell=True,
            start_new_session=True)

    print(f"*****   PID: {server_process.pid}")
    return server_process


def check_server_ready(log_path):
    """Verify that the server is ready to use.
    Issue requests until we get a correct response.
    Verify the response is from the server we just started,
      not some other server.
    """
    print("***** Checking server...")
    # Wait until server is ready.
    url = "http://localhost:8008/"
    connected = False
    attempts, max_attempts = 1, 50
    while attempts < max_attempts:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                connected = True
                break
        except requests.ConnectionError:
            attempts += 1
            sleep(0.2)

    # Verify connection.
    assert connected

    # Verify connection was made to *this* server, not
    #   a previous test run, or some other server on 8008.
    # Pause for log file to be written.
    sleep(1)
    log_text = log_path.read_text()
    assert "Error: That port is already in use" not in log_text
    assert "Watching for file changes with StatReloader" in log_text
    assert 'GET / HTTP/1.1" 200' in log_text


def stop_server(server_process):
    """Terminate the development server process.
    The main process will spawn children and maybe
      grandchildren. Terminate all these processes.
    """
    print("\n***** Stopping server...")
    if platform.system() == "Windows":
        stop_server_win(server_process)
    else:
        pgid = os.getpgid(server_process.pid)
        os.killpg(pgid, signal.SIGTERM)
        server_process.wait()

    # Print a message about the server status before exiting.
    if server_process.poll() is None:
        print("\n***** Server still running.")
        print("*****   PID:", server_process.pid)
    else:
        print("\n***** Server process terminated.")


def stop_server_win(server_process):
    """Stop server processes on Windows.
    Get the main process, then all children and grandchildren,
      and terminate all processes.
    """
    main_proc = psutil.Process(server_process.pid)
    child_procs = main_proc.children(recursive=True)

    for proc in child_procs:
        proc.terminate()

    main_proc.terminate()


def show_versions(llenv_python_cmd):
    """Show what versions of Python and Django were used."""
    cmd = f"{llenv_python_cmd} -m pip freeze"
    output = utils.run_command(cmd)

    lines = output.splitlines()
    django_version = [l for l in lines if "Django" in l][0]
    django_version = django_version.replace("==", " ")

    cmd = f"{llenv_python_cmd} --version"
    python_version = utils.run_command(cmd)

    msg = "\n***** Tested Learning Log project using:"
    msg += f"\n*****   {python_version}"
    msg += f"\n*****   {django_version}"
    print(msg)