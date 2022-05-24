from django.db import models

from aria.core.models import BaseQuerySet


class LogEntryManager(models.Manager):

    use_in_migration = True

    # constructor for creating a logging instance
    def log_update(
        self, user, content_type, object_id, content_object, change, date_of_change
    ):

        return self.model.objects.create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            content_object=content_object,
            change=change,
            date_of_change=date_of_change,
        )


class LogEntryQuerySet(BaseQuerySet):
    pass
