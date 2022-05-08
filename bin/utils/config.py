import pathlib
from typing import Optional, Dict

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent


def postgres_env(
    host: Optional[str],
    port: Optional[int],
    user: Optional[str],
    password: Optional[str],
) -> Dict[str, str]:

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
