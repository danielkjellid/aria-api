from typing import Final

from aria.forms.enums import FrontendFormElements

FORM_ELEMENT_MAPPING: Final[dict[str, str]] = {
    "string": FrontendFormElements.TEXT_INPUT,
    "text": FrontendFormElements.TEXT_INPUT,
    "integer": FrontendFormElements.NUMBER_INPUT,
    "boolean": FrontendFormElements.CHECKBOX,
    "enum": FrontendFormElements.SELECT,
    "array": FrontendFormElements.MULTISELECT,
    "file": FrontendFormElements.FILE,
    "image": FrontendFormElements.IMAGE,
    "number": FrontendFormElements.NUMBER_INPUT,
    "object": FrontendFormElements.NUMBER_INPUT,
}
