import dataclasses
import inspect
import types

import pytest
from pydantic import BaseModel

from aria.core.cache_utils import (
    _can_check_subclass,
    _is_list_with_pydantic_models,
    _is_pydantic_model,
    _pydantic_decoder,
    _pydantic_encoder,
    _pydantic_list_decoder,
    _pydantic_list_encoder,
    get_codec,
)


class MyPydanticModel(BaseModel):
    a: int
    b: int
    c: int


class MyClass(object):
    pass


class TestCoreCacheUtils:
    @pytest.mark.parametrize(
        "value,expected_codec,expected_output",
        [
            (
                MyPydanticModel(a=1, b=2, c=3),
                (_pydantic_encoder, _pydantic_decoder),
                {"a": 1, "b": 2, "c": 3},
            ),
            (
                [MyPydanticModel(a=1, b=2, c=3), MyPydanticModel(a=2, b=2, c=3)],
                (_pydantic_list_encoder, _pydantic_list_decoder),
                [{"a": 1, "b": 2, "c": 3}, {"a": 2, "b": 2, "c": 3}],
            ),
            (
                {"a": 1, "b": 2, "c": 3},
                tuple(),
                {"a": 1, "b": 2, "c": 3},
            ),
            (
                [{"a": 1, "b": 2, "c": 3}, {"a": 2, "b": 2, "c": 3}],
                tuple(),
                [{"a": 1, "b": 2, "c": 3}, {"a": 2, "b": 2, "c": 3}],
            ),
        ],
    )
    def test_cache_util__get_codec(self, value, expected_codec, expected_output):
        """
        Test that the get_codec util returns expected codec, and parses in/output
        correctly.
        """

        encoder, decoder = get_codec(type_annotation=type(value))
        encoded_value = encoder(value)
        decoded_value = decoder(encoded_value)

        # Assert that correct codec is used.
        assert encoder, decoder == expected_codec

        # Assert that we correctly encode to dicts.
        assert encoded_value == expected_output
        assert isinstance(encoded_value, type(expected_output))

        # Assert that we correctly decode back to the type instance.
        assert decoded_value == value
        assert isinstance(decoded_value, type(value))

    def test_cache_util__is_list_with_pydantic_models(self):

        # pydantic_model = MyPydanticModel(a=1, b=2, c=3)
        # assert _is_list_with_pydantic_models(type(pydantic_model)) is False

        pydantic_models_list = [
            MyPydanticModel(a=1, b=2, c=3),
            MyPydanticModel(a=2, b=2, c=3),
        ]
        assert _is_list_with_pydantic_models(pydantic_models_list) is True

        # dict_model = {"a": 1, "b": 2, "c": 3}
        # assert _is_list_with_pydantic_models(type=(dict_model)) is False
        #
        # dict_model_list = [{"a": 1, "b": 2, "c": 3}, {"a": 2, "b": 2, "c": 3}]
        # assert _is_list_with_pydantic_models(type(dict_model_list)) is False

    def test_cache_util__is_pydantic_model(self):
        assert False
