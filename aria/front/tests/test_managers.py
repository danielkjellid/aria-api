from datetime import timedelta

from django.utils import timezone

import pytest

from aria.front.models import OpeningHours
from aria.front.tests.utils import create_opening_hours, create_opening_hours_deviation

pytestmark = pytest.mark.django_db


class TestOpeningHoursQuerySetManager:

    model = OpeningHours

    def test_with_active_deviations(self, django_assert_max_num_queries):
        """
        Test that the with_active_deviations method returns expected values
        within a given query limit.
        """

        opening_hours_instance = create_opening_hours()
        create_opening_hours_deviation(
            opening_hours_id=opening_hours_instance.id,
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 4 queries:
        # - 1x for getting the opening hours instance.
        # - 1x for getting related deviation
        # - 1x for getting related time slots
        # - 1x for gettung site_message and message location.
        with django_assert_max_num_queries(4):
            opening_hours = (
                self.model.objects.filter(id=opening_hours_instance.id)
                .with_active_deviations()
                .first()
            )

        assert hasattr(opening_hours, "active_deviations")
