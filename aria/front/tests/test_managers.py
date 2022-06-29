from datetime import timedelta

from django.utils import timezone

import pytest

from aria.front.models import OpeningHours, SiteMessage
from aria.front.tests.utils import (
    create_opening_hours,
    create_opening_hours_deviation,
    create_site_message,
    create_site_message_location,
)

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


class TestSiteMessageQuerySetManager:

    model = SiteMessage

    def test_with_locations(self, django_assert_max_num_queries):
        """
        Test that the with_locations method returns expected values
        within a given query limit.
        """

        locations = [
            create_site_message_location(slug="location-1"),
            create_site_message_location(slug="location-2"),
            create_site_message_location(slug="location-3"),
        ]
        site_message_instance = create_site_message(
            locations=locations,
            show_message_at=timezone.now(),
            show_message_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 2 queries: 1 for getting site messages and 1 for prefetching
        # related locations.
        with django_assert_max_num_queries(2):
            site_message = (
                self.model.objects.filter(id=site_message_instance.id)
                .with_locations()
                .first()
            )

        assert hasattr(site_message, "related_locations")
