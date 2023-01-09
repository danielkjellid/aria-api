from ninja import Schema

from aria.forms.enums import FrontendFormElements


class FormBlockEnumOutput(Schema):
    name: str
    value: int | bool | str


class FormBlockOutput(Schema):
    id: str
    title: str
    type: str
    parent: str | None
    enum: list[FormBlockEnumOutput] | None
    default_value: int | str | bool | None
    element: FrontendFormElements
    placeholder: str | None
    help_text: str | None
    display_word_count: bool
    hidden_label: bool
    col_span: int | None


class FormSectionOutput(Schema):
    name: str
    blocks: list[str]


class FormOutput(Schema):
    key: str
    is_multipart_form: bool
    expects_list: bool
    required: list[str]
    sections: list[FormSectionOutput]
    blocks: list[FormBlockOutput]
