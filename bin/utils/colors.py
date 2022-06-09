import functools


def _color(value: str, color_code: str) -> str:
    return f"\033[{color_code}m{value}\033[0m"


red = functools.partial(_color, color_code="91")
magenta = functools.partial(_color, color_code="35")
gray = functools.partial(_color, color_code="37")
