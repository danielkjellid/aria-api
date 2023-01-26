from enum import Enum


class FrontendFormElements(Enum):
    TEXT_INPUT = "textInput"
    NUMBER_INPUT = "numberInput"
    CHECKBOX = "checkbox"
    SELECT = "select"
    MULTISELECT = "multiselect"
    LIST_BOX_FILTER = "listBoxFilter"
    LIST_BOX_FILTER_NUMBER = "listBoxFilterNumber"
    EDITOR = "editor"
    ACTION = "action"
    IMAGE = "image"
    FILE = "file"
