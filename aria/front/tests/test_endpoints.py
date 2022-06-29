import json
from datetime import timedelta

from django.utils import timezone

import pytest

from aria.core.tests.utils import create_site
from aria.front.tests.utils import (
    create_opening_hours,
    create_opening_hours_deviation,
    create_site_message,
)

pytestmark = pytest.mark.django_db


class TestPublicFrontEndoints:

    BASE_ENDPOINT = "/api/front"

    def test_opening_hours_detail_api(
        self, django_assert_max_num_queries, anonymous_client
    ) -> None:
        """
        Test retrieving opening hours for a site from an anonymous client returns
        a valid response.
        """

        site = create_site()
        opening_hours = create_opening_hours(site=site)

        expected_response = {
            "id": opening_hours.id,
            "human_readable_time_slots": [
                {
                    "days": "Mandag - Torsdag",
                    "time_slot": "09:00 - 17:00",
                    "is_closed": False,
                },
                {"days": "Fredag", "time_slot": "09:00 - 16:00", "is_closed": False},
                {"days": "Lørdag", "time_slot": "10:00 - 15:00", "is_closed": False},
                {"days": "Søndag", "time_slot": None, "is_closed": True},
            ],
        }

        # Uses 4 queries:
        # - 1x for getting site.
        # - 1x for getting opening hours instance.
        # - 1x for getting related time slots.
        # - 1x for getting related deviations.
        with django_assert_max_num_queries(4):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/opening-hours/{site.id}/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        create_opening_hours_deviation(
            opening_hours_id=opening_hours.id,
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        expected_deviation_response = {
            "id": opening_hours.id,
            "human_readable_time_slots": [
                {
                    "days": "Mandag, Tirsdag og Torsdag",
                    "time_slot": "09:00 - 17:00",
                    "is_closed": False,
                },
                {"days": "Onsdag og Søndag", "time_slot": None, "is_closed": True},
                {"days": "Fredag", "time_slot": "09:00 - 16:00", "is_closed": False},
                {"days": "Lørdag", "time_slot": "10:00 - 15:00", "is_closed": False},
            ],
        }

        # Uses 6 queries:
        # - 1x for getting site.
        # - 1x for getting opening hours instance.
        # - 1x for getting related time slots.
        # - 1x for getting related deviations.
        # - 1x for getting deviation time slots
        # - 1x for getting deviation template site message and location.
        with django_assert_max_num_queries(6):
            deviation_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/opening-hours/{site.id}/"
            )

        actual_deviation_response = json.loads(deviation_response.content)

        assert response.status_code == 200
        assert actual_deviation_response == expected_deviation_response

    def test_site_messages_active_list_api(
        self, django_assert_max_num_queries, anonymous_client
    ) -> None:
        """
        Test retrieving active site messages for a site from an anonymous client
        returns a valid response.
        """

        site = create_site()
        site_message_1 = create_site_message(
            site=site,
            show_message_at=timezone.now(),
            show_message_to=timezone.now() + timedelta(minutes=10),
        )
        site_message_2 = create_site_message(
            site=site,
            show_message_at=timezone.now(),
            show_message_to=timezone.now() + timedelta(minutes=15),
        )
        # Expired message.
        create_site_message(
            site=site,
            show_message_at=timezone.now() - timedelta(minutes=10),
            show_message_to=timezone.now() - timedelta(minutes=5),
        )

        expected_response = [
            {
                "text": site_message_1.text,
                "message_type": site_message_1.message_type,
                "locations": ["test-location"],
                "show_message_at": site_message_1.show_message_at.isoformat(),
                "show_message_to": site_message_1.show_message_to.isoformat(),
            },
            {
                "text": site_message_2.text,
                "message_type": site_message_2.message_type,
                "locations": ["test-location"],
                "show_message_at": site_message_2.show_message_at.isoformat(),
                "show_message_to": site_message_2.show_message_to.isoformat(),
            },
        ]

        # Uses 3 queries:
        # - 1x for getting the site.
        # - 1x for getting active site messages.
        # - 1x for getting related site message locations.
        with django_assert_max_num_queries(3):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/site-messages/{site.id}/active/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response
