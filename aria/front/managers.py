from typing import TYPE_CHECKING

from aria.core.models import BaseQuerySet

if TYPE_CHECKING:
    pass


class OpeningHoursQuerySet(BaseQuerySet["models.OpeningHours"]):
    pass


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
    pass
