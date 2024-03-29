from typing import TYPE_CHECKING

from django.db.models import Prefetch
from django.utils import timezone

from aria.core.managers import BaseQuerySet

if TYPE_CHECKING:
    from aria.front import models


class OpeningHoursQuerySet(BaseQuerySet["models.OpeningHours"]):
    def with_active_deviations(self) -> BaseQuerySet["models.OpeningHours"]:
        """
        Prefetch active deviations related to an opening hours instance.
        """
        from aria.front.models import OpeningHoursDeviation

        active_deviations = (
            OpeningHoursDeviation.objects.filter(
                active_at__lte=timezone.now(), active_to__gt=timezone.now()
            )
            .select_related("template", "template__site_message")
            .prefetch_related("time_slots", "template__site_message__locations")
        )

        prefetched_deviations = Prefetch(
            "deviations", queryset=active_deviations, to_attr="active_deviations"
        )

        return self.prefetch_related(prefetched_deviations)


class OpeningHoursTimeSlotQuerySet(BaseQuerySet["models.OpeningHoursTimeSlot"]):
    pass


class OpeningHoursDeviationQuerySet(BaseQuerySet["models.OpeningHoursDeviation"]):
    pass


class OpeningHoursDeviationTemplateQuerySet(
    BaseQuerySet["models.OpeningHoursDeviationTemplate"]
):
    pass


class SiteMessageLocationQuerySet(BaseQuerySet["models.SiteMessageLocation"]):
    pass


class SiteMessageQuerySet(BaseQuerySet["models.SiteMessage"]):
    def with_locations(self) -> BaseQuerySet["models.SiteMessage"]:
        """
        Prefetch site message locations related to a site message. Sets the
        prefetched values attribute as "related_locations"
        """
        return self.prefetch_related(Prefetch("locations", to_attr="related_locations"))
