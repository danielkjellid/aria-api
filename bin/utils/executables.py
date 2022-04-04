import subprocess
import pathlib
from typing import Optional, Union
import os
import sys
from .config import PROJECT_ROOT


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