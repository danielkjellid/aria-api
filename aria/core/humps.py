import re
from collections.abc import Mapping
from typing import Any, Callable

ACRONYM_RE = re.compile(r"([A-Z]+)$|([A-Z]+)(?=[A-Z0-9])")
PASCAL_RE = re.compile(r"([^\-_\s]+)")
SPLIT_RE = re.compile(r"([\-_\s]*[A-Z]+?[^A-Z\-_\s]*[\-_\s]*)")
UNDERSCORE_RE = re.compile(r"(?<=[^\-_\s])[\-_\s]+[^\-_\s]")


def _is_none(
    _in: str | list[Any] | dict[str, Any] | None
) -> str | list[Any] | dict[str, Any]:
    """
    Determine if the input is None.
    """

    return "" if _in is None else _in


def _fix_abbreviations(string: str) -> str:
    """
    Rewrite incorrectly cased acronyms, initialisms, and abbreviations,
    allowing them to be decamelized correctly. For example, given the string
    "APIResponse", this function is responsible for ensuring the output is
    "api_response" instead of "a_p_i_response".
    """

    return ACRONYM_RE.sub(lambda m: m.group(0).title(), string)


def _separate_words(string: str, separator: str = "_") -> str:
    """
    Split words that are separated by case differentiation.
    """

    return separator.join(s for s in SPLIT_RE.split(string) if s)


def _process_keys(
    str_or_iter: str | list[Any] | dict[str, Any], fn: Callable[[Any], Any]
) -> str | list[Any] | dict[str, Any]:
    if isinstance(str_or_iter, list):
        return [_process_keys(k, fn) for k in str_or_iter]
    if isinstance(str_or_iter, Mapping):
        return {fn(k): _process_keys(v, fn) for k, v in str_or_iter.items()}
    return str_or_iter


def is_camelcase(str_or_iter: str | list[Any] | dict[str, Any]) -> bool:
    """
    Determine if a string, dict, or list of dicts is camel case.
    """

    if str_or_iter == camelize(str_or_iter):
        return True

    return False


def is_snakecase(str_or_iter: str | list[Any] | dict[str, Any]) -> bool:
    """
    Determine if a string, dict, or list of dicts is snake case.
    """

    if str_or_iter == decamelize(str_or_iter):
        return True

    return False


def camelize(
    str_or_iter: str | list[Any] | dict[str, Any]
) -> str | list[Any] | dict[str, Any]:
    """
    Convert a string, dict, or list of dicts to camel case.
    """

    if isinstance(str_or_iter, (list, Mapping)):
        return _process_keys(str_or_iter, camelize)

    s = str(_is_none(str_or_iter))
    if s.isupper() or s.isnumeric():
        return str_or_iter

    if len(s) != 0 and not s[:2].isupper():
        s = s[0].lower() + s[1:]

    # For string "hello_world", match will contain
    #             the regex capture group for "_w".
    return UNDERSCORE_RE.sub(lambda m: m.group(0)[-1].upper(), s)


def decamelize(
    str_or_iter: str | list[Any] | dict[str, Any]
) -> str | list[Any] | dict[str, Any]:
    """
    Convert a string, dict, or list of dicts to snake case.
    """

    if isinstance(str_or_iter, (list, Mapping)):
        return _process_keys(str_or_iter, decamelize)

    s = str(_is_none(str_or_iter))
    if s.isupper() or s.isnumeric():
        return str_or_iter

    return _separate_words(_fix_abbreviations(s)).lower()
