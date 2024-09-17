from dataclasses import dataclass

from pydantic import BaseModel

from aria.forms.helpers import (
    get_inner_list_type,
    is_list,
    is_pydantic_model,
    unwrap_item_type_from_list,
)


class MyModel(BaseModel):
    val: int


@dataclass(frozen=True)
class MyDataclass:
    val: int


class TestFormsUtilHelpers:
    def test_helper_is_list(self):
        """
        Test that the is_list helper correctly outputs when a type annotation is a list.
        """

        assert is_list(type_annotation=list[MyModel]) is True
        assert is_list(type_annotation=list[MyDataclass]) is True

        assert is_list(type_annotation=tuple[MyModel]) is False
        assert is_list(type_annotation=tuple[MyDataclass]) is False

        assert is_list(type_annotation=set[MyModel]) is False
        assert is_list(type_annotation=set[MyDataclass]) is False

    def test_helper_is_pydantic_model(self):
        """
        Test that the is_pydantic_model helper correctly outputs when a type annotation
        is a pydantic model.
        """

        assert is_pydantic_model(type_annotation=MyModel) is True
        assert is_pydantic_model(type_annotation=MyDataclass) is False

    def test_helper_get_inner_list_type(self):
        """
        Test that the get_inner_list_type helper correctly retrieves the inner type
        when both a list and the type is passed.
        """

        class_type, is_in_list = get_inner_list_type(type_annotation=MyModel)
        assert class_type is MyModel
        assert is_in_list is False

        class_type, is_in_list = get_inner_list_type(type_annotation=list[MyModel])
        assert class_type is MyModel
        assert is_in_list is True

        class_type, is_in_list = get_inner_list_type(type_annotation=MyDataclass)
        assert class_type is MyDataclass
        assert is_in_list is False

        class_type, is_in_list = get_inner_list_type(type_annotation=list[MyDataclass])
        assert class_type is MyDataclass
        assert is_in_list is True

    def test_helper_unwrap_item_type_from_list(self):
        """
        Test that the unwrap_item_type_from_list helper correctly retrieves the inner
        type from a passed list of types.
        """

        assert unwrap_item_type_from_list(type_annotation=list[MyModel]) == MyModel
        assert unwrap_item_type_from_list(type_annotation=list[int]) == int
        assert (
            unwrap_item_type_from_list(type_annotation=list[MyDataclass]) == MyDataclass
        )
