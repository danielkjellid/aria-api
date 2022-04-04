import subprocess
from datetime import datetime
from .colors import gray

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
    
    
def print_with_time(value: str, end="\n", flush=False) -> None:
    _time = f"[{datetime.now():%H:%M:%S}]"
    print(f"{gray(_time)} {value}", end=end, flush=flush)