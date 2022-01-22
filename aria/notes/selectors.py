from typing import Union
from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from aria.notes.models import NoteEntry


def notes_for_instance_list(*, instance: Model) -> Union[QuerySet, NoteEntry]:
    """
    Generic get service meant to be reused in local get services
    For example:

    def notes_for_instance_list(*, user: User) -> Union[Queryset, NoteEntry]:
        return notes_for_instance_get(instance=user)

    Return value: List of notes belloning to instance, if any.
    """

    content_type = ContentType.objects.get_for_model(instance)

    return NoteEntry.objects.filter(content_type=content_type, object_id=instance.id)
