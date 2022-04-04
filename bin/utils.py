import functools
import subprocess
import pathlib
from typing import Optional, Union, Iterator
import os
import sys
import contextlib
from datetime import datetime


PROJECT_ROOT = pathlib.Path(__file__).parent.parent

###################
# Console helpers #
###################


def _color(value: str, color_code: str) -> str:
    return f"\033[{color_code}m{value}\033[0m"


red = functools.partial(_color, color_code="91")
magenta = functools.partial(_color, color_code="35")
gray = functools.partial(_color, color_code="37")


def print_with_time(value: str, end="\n", flush=False) -> None:
    _time = f"[{datetime.now():%H:%M:%S}]"
    print(f"{gray(_time)} {value}", end=end, flush=flush)


#####################
# Runnable commands #
#####################

def run_cli_command(
    *args: Union[str, pathlib.Path],
    env: Optional[dict[str, str]] = None,
    capture: bool = True,
    inp: Optional[str] = None,
) -> str:
    """
    Execute a specific command.
    """

    process = subprocess.run(
        args, check=True, capture_output=capture, encoding="utf-8", env=env, input=inp
    )

    return process.stdout


def run_postgres_command(
    command: str,
    *command_args: Union[str, pathlib.Path],
    user: Optional[str],
    host: Optional[str],
    port: Optional[int],
    password: Optional[str],
) -> None:

    args: list[Union[str, pathlib.Path]] = [command]

    # If no function arguments are given, fall back to env vars.

    postgres_user = user if user else os.getenv("POSTGRES_USER")
    if postgres_user:
        args.extend(["--user", postgres_user])

    postgres_host = host if host else os.getenv("POSTGRES_HOST")
    if postgres_host:
        args.extend(["--host", postgres_host])

    postgres_port = port if port else os.getenv("POSTGRES_PORT")
    if postgres_port:
        args.extend(["--port", str(postgres_port)])

    postgres_password = password if password else os.getenv("POSTGRES_PASSWORD")

    args.extend(command_args)

    env = {**os.environ}
    if postgres_password:
        env["PGPASSWORD"] = postgres_password

    run_cli_command(*args, env=env)
    
    
def run_management_command(
    command: str,
    *command_args: Union[str, pathlib.Path],
    db_name: str,
    env_vars: dict[str, str] = {},
):

    if db_name:
        env_vars["POSTGRES_DB"] = db_name
        
    run_cli_command(
        sys.executable,
        PROJECT_ROOT / "manage.py",
        command,
        *command_args,
        env={**os.environ, **env_vars},
    )


################
# Helper utils #
################

def postgres_env(
    host: Optional[str],
    port: Optional[int],
    user: Optional[str],
    password: Optional[str],
) -> dict[str, str]:

    env = {}

    if host:
        env["POSTGRES_HOST"] = host

    if port:
        env["POSTGRES_PORT"] = port

    if user:
        env["POSTGRES_USER"] = user

    if password:
        env["POSTGRES_PASSWORD"] = password

    return env


def check_exit_code(*args: str, expected_result: int = 0) -> bool:
    try:
        return (
            subprocess.run(
                args, check=False, capture_output=True
            ).returncode
            == expected_result
        )
    except FileNotFoundError:
        return False
    
    
##################
# Error handling #
##################

class Cancel(RuntimeError):
    # pylint: disable=redefined-builtin
    def __init__(self, *, description: str, help: str = "") -> None:
        super().__init__()
        self.description = description
        self.help = help
        

@contextlib.contextmanager
def action_runner(
    *,
    description: str,
    exit_on_failure: bool = True,
    error_message: Optional[str] = None,
) -> Iterator[None]:
    """
    A context manager that handles subprocess errors.
    """

    print_with_time(magenta(f"{description} ... "), end="", flush=True)

    try:
        yield
        print("✅")
    except subprocess.CalledProcessError as e:
        print("❌")
        print(
            red(
                f"An error occured while running "
                f'"{" ".join(str(arg) for arg in e.args)}"'
            )
        )

        if e.stdout:
            print("-" * 20 + red(" stdout ") + "-" * 20)
            print(e.stdout.strip())
            print("-" * 48)

        if e.stderr:
            print("-" * 20 + red(" stderr ") + "-" * 20)
            print(e.stderr.strip())
            print("-" * 48)

        if not exit_on_failure:
            raise
        if error_message:
            sys.exit(error_message)
        sys.exit(1)
    except Cancel as e:
        print("❌")
        print(red(e.description))
        if e.help:
            print(e.help)
        if not exit_on_failure:
            raise
        sys.exit(1)
    