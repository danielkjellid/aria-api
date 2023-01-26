import typing

import pydantic


def is_list(*, type_annotation: type) -> bool:
    return typing.get_origin(type_annotation) is list


def is_pydantic_model(*, type_annotation: type) -> bool:
    return issubclass(type_annotation, pydantic.BaseModel) or (
        hasattr(type_annotation, "__pydantic_model__")
        and issubclass(type_annotation.__pydantic_model__, pydantic.BaseModel)
    )


def get_inner_list_type(*, type_annotation: type) -> tuple[type, bool]:
    is_lst = is_list(type_annotation=type_annotation)
    if is_lst:
        type_annotation = unwrap_item_type_from_list(type_annotation=type_annotation)
    return type_annotation, is_lst


def unwrap_item_type_from_list(*, type_annotation: type) -> type:
    return typing.get_args(type_annotation)[0]
