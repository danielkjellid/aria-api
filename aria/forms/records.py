from pydantic import BaseModel


class FormBlockInputAttrsRecord(BaseModel):
    type: str
    placeholder: str


class FormBlockInputRecord(BaseModel):
    type: str
    label: str
    help_text: str | None
    enum: list[str] | list[int] | None = None


class FormBlockRecord(BaseModel):
    name: str


class FormRecord(BaseModel):
    key: str
    title: str
    description: str
    blocks: FormBlockRecord
