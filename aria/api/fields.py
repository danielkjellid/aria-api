from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic.fields import FieldInfo, UndefinedType

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, NoArgAnyCallable

from aria.forms.enums import FrontendFormElements

Undefined = UndefinedType()


def FormField(
    default: Any = Undefined,
    *,
    default_factory: Optional["NoArgAnyCallable"] = None,
    alias: str = None,
    title: str = None,
    description: str = None,
    exclude: Union["AbstractSetIntStr", "MappingIntStrAny", Any] = None,
    include: Union["AbstractSetIntStr", "MappingIntStrAny", Any] = None,
    const: bool = None,
    gt: float = None,
    ge: float = None,
    lt: float = None,
    le: float = None,
    multiple_of: float = None,
    allow_inf_nan: bool = None,
    max_digits: int = None,
    decimal_places: int = None,
    min_items: int = None,
    max_items: int = None,
    unique_items: bool = None,
    min_length: int = None,
    max_length: int = None,
    allow_mutation: bool = True,
    regex: str = None,
    discriminator: str = None,
    repr: bool = True,
    help_text: str | None = None,
    element: FrontendFormElements = None,
    placeholder: str = None,
    display_word_count: bool = False,
    hidden_label: bool = False,
    col_span: int = None,
    allow_set_primary_image: bool = False,
    allow_set_filter_image: bool = False,
    **extra: Any,
) -> Any:

    field_info = FieldInfo(
        default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        discriminator=discriminator,
        repr=repr,
        help_text=help_text,
        element=element,
        placeholder=placeholder,
        display_word_count=display_word_count,
        hidden_label=hidden_label,
        col_span=col_span,
        allow_set_primary_image=allow_set_primary_image,
        allow_set_filter_image=allow_set_filter_image,
        **extra,
    )
    field_info._validate()
    return field_info
