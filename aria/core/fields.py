import os
from io import BytesIO
from typing import Any, Dict, Iterable, Mapping

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.forms import CheckboxSelectMultiple

from aria.files.utils import image_resize


class ArraySelectMultiple(CheckboxSelectMultiple):
    def value_omitted_from_data(  # type: ignore
        self, data: Dict[str, Any], files: Mapping[str, Iterable[Any]], name: str
    ) -> bool:
        return False


class ChoiceArrayField(ArrayField):  # type: ignore
    """
    Implementation from here: https://gist.github.com/danni/f55c4ce19598b2b345ef
    A field that allows us to store an array of choices.
    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.
    Usage:
        choices = ChoiceArrayField(models.CharField(max_length=...,
                                                    choices=(...,)),
                                                    default=[...])
    """

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore

        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": ArraySelectMultiple,
            "required": not self.null and not self.default,
        }
        defaults.update(kwargs)

        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)


class RezisedImageFieldFile(ImageField.attr_class):
    def save(self, name: str, content: BytesIO, save: bool = True) -> None:
        if self.width is None or self.height is None:
            raise ValueError("Both width and height needs to be specified.")

        image = image_resize(
            image=content, max_width=self.width, max_height=self.height
        )

        return super(RezisedImageFieldFile, self).save(
            name=name, content=image, save=True
        )


class ResizedImageField(ImageField):
    """
    A field that automatically resizes images before save.
    """

    attr_class = RezisedImageFieldFile

    def __init__(
        self, verbose_name: str | None = None, name: str | None = None, **kwargs: Any
    ) -> None:
        self.width = kwargs.pop("width", None)
        self.height = kwargs.pop("height", None)

        super(ResizedImageField, self).__init__(
            verbose_name=verbose_name,
            name=name,
            **kwargs,
        )

    # def save(self, name: str, content: BytesIO, save: bool = True) -> None:
    #     raise RuntimeError("test")
    #     if self.width is None or self.height is None:
    #         raise ValueError("Both width and height needs to be specified.")
    #     print("this fires")
    #     image = image_resize(
    #         image=content, max_width=self.width, max_height=self.height
    #     )
    #
    #     return super().save(name=name, content=image, save=save)
