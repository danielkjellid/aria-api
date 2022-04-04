import subprocess
from typing import Optional, Iterator
import sys
import contextlib
from .colors import red, gray
from .helpers import print_with_time


class Cancel(RuntimeError):
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

    print_with_time(gray(f"{description}... "), end="", flush=True)

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
