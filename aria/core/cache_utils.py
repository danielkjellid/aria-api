import inspect
import types
import typing
from types import NoneType, UnionType
from typing import Any, Callable, Type, TypeVar, Union

from pydantic import BaseModel, json, parse_obj_as, parse_raw_as

T = TypeVar("T", bound=BaseModel)


def get_codec(
    *, type_annotation: Type[Any]
) -> tuple[Callable[[Any], Any], Callable[[Any], Any]]:
    """
    Get an encoder and decoder for the given type. This is mainly to handle
    pydantic models, which we don't want to pickle when caching, because that can
    lead to weird behaviour. By default Django will pickle any value in the
    cache, but when unpickling objects they are stored to the state they were in
    when they were picked, not the current state in code (e.g. if you add a new
    field with a default it won't be set on the unpicked object).
    """

    if _is_pydantic_model(type_annotation):
        print("hits here")
        return _pydantic_encoder(type_annotation), _pydantic_decoder(type_annotation)

    if _is_list_with_pydantic_models(type_annotation):
        print("hits here instead")
        return _pydantic_list_encoder(type_annotation), _pydantic_list_decoder(
            type_annotation
        )

    return lambda value: value, lambda value: value


def _can_check_subclass(type_annotation: type) -> bool:
    if (
        not inspect.isclass(type_annotation)
        or type(type_annotation) is types.GenericAlias
    ):
        return False

    return True


def _is_list_with_pydantic_models(type_annotation: type) -> bool:

    origin = typing.get_origin(type_annotation)
    args = typing.get_args(type_annotation)

    return (
        origin is list
        and len(args) == 1
        and all(
            issubclass(arg, BaseModel) if _can_check_subclass(arg) else False
            for arg in args
        )
    )


def _pydantic_list_decoder(
    type_annotation: type,
) -> Callable[[str | None], list[T] | None]:

    decoder = _pydantic_decoder(type_annotation)

    def decode_pydantic_list(value: str | None):
        return [decoder(item) for item in value] if value else value

    return decode_pydantic_list


def _pydantic_list_encoder(
    type_annotation: type,
) -> Callable[[list[T] | None], str | None]:

    encoder = _pydantic_encoder(type_annotation)

    def encode_pydantic_list(value: str | None):
        return (
            [encoder(item) if _is_pydantic_model(item) else None for item in value]
            if value
            else value
        )

    return encode_pydantic_list


def _is_pydantic_model(type_annotation: type) -> bool:

    origin = typing.get_origin(type_annotation)
    args = typing.get_args(type_annotation)

    # Make sure the type annotation is an actual class we can run
    # issubclass on.
    if not _can_check_subclass(type_annotation):
        print("returns false")
        return False

    return (
        # Plain pydantic model.
        issubclass(type_annotation, BaseModel)
        # Or an optional pydantic model.
        or (
            origin in (UnionType, Union)
            and NoneType in args
            and any(issubclass(arg, BaseModel) for arg in args)
        )
    )


def _pydantic_decoder(typ: Type[T]) -> Callable[[str | None], T | None]:
    def decode_pydantic_model(value: str | None) -> T | None:
        if value is None:
            return None

        if isinstance(value, str):
            return parse_raw_as(typ, value)

        return parse_obj_as(typ, value)

    return decode_pydantic_model


def _pydantic_encoder(typ: Type[T]) -> Callable[[T | None], str | None]:
    def encode_pydantic_model(obj: T | None) -> str | None:
        return json.pydantic_encoder(obj) if obj else None

    return encode_pydantic_model
