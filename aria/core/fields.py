from typing import Any, Dict, Iterable, Mapping

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.forms import CheckboxSelectMultiple


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
