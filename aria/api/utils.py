import re
from typing import Any, Pattern

from django.utils.translation import activate, deactivate, gettext as _

from aria.api.types import PydanticErrorDict

MESSAGE_TEMPLATE = {
    "field required": _("field required"),
    "none is not an allowed value": _("none is not an allowed value"),
    "value is not none": _("value is not none"),
    "This field cannot be blank.": _("This field cannot be blank."),
    "This password is entirely numeric.": _("This password is entirely numeric."),
    "This password is too common.": _("This password is too common."),
    "The password is too similar to the %(verbose_name)s.": _(
        "The password is too similar to the %(verbose_name)s."
    ),
    "This password is too short. It must contain at least %(min_length)d characters.": _(
        "This password is too short. It must contain at least %(min_length)d characters."
    ),
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
    try:
        translated_string = _(MESSAGE_TEMPLATE[key]).replace("{}", placeholder)
    except KeyError:
        translated_string = key
    deactivate()

    return translated_string


def translate_pydantic_validation_messages(
    errors: list[PydanticErrorDict] | list[dict[str, Any]], locale: str
) -> list[PydanticErrorDict]:
    """
    Loop over all messages in validation output and translate messages.
    """

    return [
        {
            **error,  # type: ignore
            "msg": _translate(message=error["msg"], locale=locale),
        }
        for error in errors
    ]
