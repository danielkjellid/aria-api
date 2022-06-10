import dataclasses
from typing import Callable, Type, Union

import dacite


def get_codec(*, type_annotation: Type) -> tuple[Callable, Callable]:
    """
    Get an encoder and decoder for the given type. This is mainly to handle
    dataclasses, which we don't want to pickle when caching, because that can
    lead to weird behaviour. By default Django will pickle any value in the
    cache, but when unpickling objects they are stored to the state they were in
    when they were picked, not the current state in code (e.g. if you add a new
    field with a default it won't be set on the unpicked object).
    """

    if dataclasses.is_dataclass(type_annotation):
        return _dataclass_encoder(type_annotation), _dataclass_decoder(type_annotation)

    if _is_optional_dataclass(type_annotation):
        _type = next(
            arg for arg in type_annotation.__args__ if dataclasses.is_dataclass(arg)
        )
        return _dataclass_encoder(_type), _dataclass_decoder(_type)

    if _is_list_with_dataclass(type_annotation):
        _type = type_annotation.__args__[0]
        return _dataclass_list_encoder(_type), _dataclass_list_decoder(_type)

    return lambda value: value, lambda value: value


def _is_list_with_dataclass(type_annotation: Type) -> bool:

    origin = getattr(type_annotation, "__origin__", None)
    args = getattr(type_annotation, "__args__", None)

    return (
        origin is list
        and isinstance(args, tuple)
        and len(args) == 1
        and dataclasses.is_dataclass(args[0])
    )


def _is_optional_dataclass(type_annotation: Type) -> bool:

    origin = getattr(type_annotation, "__origin__", None)
    args = getattr(type_annotation, "__args__", None)

    return (
        origin is Union
        and isinstance(args, tuple)
        and type(None) in args
        and any(dataclasses.is_dataclass(arg) for arg in args)
    )


def _dataclass_decoder(type_annotation: Type) -> Callable:
    def decode_dataclass(value):
        return dacite.from_dict(type_annotation, value) if value else None

    return decode_dataclass


def _dataclass_encoder(type_annotation: Type) -> Callable:
    def encode_dataclass(value):
        return dataclasses.asdict(value) if value else None

    return encode_dataclass


def _dataclass_list_decoder(type_annotation: Type) -> Callable:

    decoder = _dataclass_decoder(type_annotation)

    def decode_dataclass_list(value):
        return [decoder(item) for item in value] if value else value

    return decode_dataclass_list


def _dataclass_list_encoder(type_annotation: Type) -> Callable:
    def encode_dataclass_list(value):
        return (
            [dataclasses.asdict(item) if item else None for item in value]
            if value
            else value
        )

    return encode_dataclass_list
