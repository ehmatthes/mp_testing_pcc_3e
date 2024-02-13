import os, shutil, subprocess, signal
from time import sleep
from pathlib import Path

import requests

import utils
from resources.ll_e2e_tests import run_e2e_test


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

    # Make migrations, call check.
    cmd = f"{llenv_python_cmd} manage.py migrate"
    output = utils.run_command(cmd)
    assert "Operations to perform:\n  Apply all migrations: admin, auth, contenttypes, learning_logs, sessions\nRunning migrations:\n  Applying contenttypes.0001_initial... OK\n  Applying auth.0001_initial... OK\n  Applying admin.0001_initial... OK\n  Applying admin.0002_logentry_remove_auto_add... OK\n  Applying admin.0003_logentry_add_action_flag_choices... OK\n  Applying contenttypes.0002_remove_content_type_name... OK\n  Applying auth.0002_alter_permission_name_max_length... OK\n  Applying auth.0003_alter_user_email_max_length... OK\n  Applying auth.0004_alter_user_username_opts... OK\n  Applying auth.0005_alter_user_last_login_null... OK\n  Applying auth.0006_require_contenttypes_0002... OK\n  Applying auth.0007_alter_validators_add_error_messages... OK\n  Applying auth.0008_alter_user_username_max_length... OK\n  Applying auth.0009_alter_user_last_name_max_length... OK\n  Applying auth.0010_alter_group_name_max_length... OK\n  Applying auth.0011_update_proxy_permissions... OK\n  Applying auth.0012_alter_user_first_name_max_length... OK\n  Applying learning_logs.0001_initial... OK\n  Applying learning_logs.0002_entry... OK\n  Applying learning_logs.0003_topic_owner... OK\n  Applying sessions.0001_initial... OK" in output

    cmd = f"{llenv_python_cmd} manage.py check"
    output = utils.run_command(cmd)
    assert "System check identified no issues (0 silenced)." in output

    # Start development server.
    #   To verify it's not running after the test:
    #   macOS: `$ ps aux | grep runserver`
    #
    # Log to file, so we can verify we haven't connected to a
    #   previous server process, or an unrelated one.
    #   shell=True is necessary for redirecting output.
    #   start_new_session=True is required to terminate
    #   the process group.
    runserver_log = dest_dir / "runserver_log.txt"
    cmd = f"{llenv_python_cmd} manage.py runserver 8008"
    cmd += f" > {runserver_log} 2>&1"
    server_process = subprocess.Popen(cmd, shell=True,
            start_new_session=True)

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
    log_text = runserver_log.read_text()
    assert "Error: That port is already in use" not in "log_text"
    assert "Watching for file changes with StatReloader" in log_text
    assert 'GET / HTTP/1.1" 200' in log_text

    try:
        run_e2e_test("http://localhost:8008/")
    except AssertionError as e:
        raise e
    finally:
        # Terminate the development server process.
        #   There will be several child processes, 
        #   so the process group needs to be terminated.
        print("\n***** Stopping server...")
        pgid = os.getpgid(server_process.pid)
        os.killpg(pgid, signal.SIGTERM)
        server_process.wait()

        # Print a message about the server status before exiting.
        if server_process.poll() is None:
            print("\n***** Server still running.")
            print("*****   PID:", server_process.pid)
        else:
            print("\n***** Server process terminated.")