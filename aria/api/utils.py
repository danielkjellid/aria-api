import re
from typing import Any, Pattern

from django.utils.translation import activate, deactivate, gettext as _

MESSAGE_TEMPLATE = {
    "field required": _("field required"),
    "none is not an allowed value": _("none is not an allowed value"),
    "value is not none": _("value is not none"),
}


def _init_translation_pattern() -> Pattern[str]:
    """
    Split MESSAGE TEMPLATE dict into a string we can search later on.
    """
    pattern = re.compile(
        "|".join(
            "({})".format(  # pylint: disable=consider-using-f-string
                i.replace("{}", "(.+)")
            )
            for i in MESSAGE_TEMPLATE
        )
    )

    return pattern


def _translate(message: str, locale: str) -> str:
    """
    Find matching key in template and replace it with translated string.
    """

    key = message
    placeholder = ""
    searched = _init_translation_pattern().search(message)

    if searched:
        groups = searched.groups()
        index = groups.index(message)

        if len(groups) > index + 1:
            placeholder = groups[index + 1]
        elif len(groups) > index:
            placeholder = groups[index]

        placeholder = placeholder or ""

        if placeholder and key != placeholder:
            key = key.replace(placeholder, "{}")

    # Activate locale passed by request to get translated string.
    activate(locale)
    translated_string = _(MESSAGE_TEMPLATE[key]).replace("{}", placeholder)
    deactivate()

    return translated_string


def translate_pydantic_validation_messages(
    errors: list[dict[str, Any]], locale: str
) -> list[dict[str, str]]:
    """
    Loop over all messages in validation output and translate messages.
    """

    return [
        {
            **error,
            "msg": _translate(message=error["msg"], locale=locale),
        }
        for error in errors
    ]
