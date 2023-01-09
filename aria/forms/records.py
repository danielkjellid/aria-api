from typing import Any

from pydantic import BaseModel

from aria.forms.enums import FrontendFormElements


class FormSectionRecord(BaseModel):
    name: str
    blocks: list[str]


class FormBlockEnumRecord(BaseModel):
    name: str
    value: int | bool | str


class FormBlockRecord(BaseModel):
    id: str
    title: str | None
    type: str | None
    enum: list[FormBlockEnumRecord] | None
    default: int | str | bool | None
    element: FrontendFormElements
    placeholder: str | None


class FormRecord(BaseModel):
    key: str
    is_multipart_form: bool = False
    expects_list: bool = False
    required: list[str]
    sections: list[FormSectionRecord]
    blocks: list[FormBlockRecord]
