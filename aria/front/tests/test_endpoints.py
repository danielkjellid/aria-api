import json
from datetime import timedelta

import pytest
from django.utils import timezone

from aria.front.tests.utils import (
    create_opening_hours,
    create_opening_hours_deviation,
    create_site_message,
)

pytestmark = pytest.mark.django_db


class TestPublicFrontEndoints:

    BASE_ENDPOINT = "/api/v1/front"

    def test_opening_hours_detail_api(
        self, django_assert_max_num_queries, anonymous_client
    ) -> None:
        """
        Test retrieving opening hours for a site from an anonymous client returns
        a valid response.
        """

        opening_hours = create_opening_hours()

        expected_response = {
            "id": opening_hours.id,
            "humanReadableTimeSlots": [
                {
                    "days": "Mandag - Torsdag",
                    "timeSlot": "09:00 - 17:00",
                    "isClosed": False,
                },
                {"days": "Fredag", "timeSlot": "09:00 - 16:00", "isClosed": False},
                {"days": "Lørdag", "timeSlot": "10:00 - 15:00", "isClosed": False},
                {"days": "Søndag", "timeSlot": None, "isClosed": True},
            ],
        }

        # Uses 3 queries:
        # - 1x for getting opening hours instance.
        # - 1x for getting related time slots.
        # - 1x for getting related deviations.
        with django_assert_max_num_queries(3):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/opening-hours/")

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
            "humanReadableTimeSlots": [
                {
                    "days": "Mandag, Tirsdag og Torsdag",
                    "timeSlot": "09:00 - 17:00",
                    "isClosed": False,
                },
                {"days": "Onsdag og Søndag", "timeSlot": None, "isClosed": True},
                {"days": "Fredag", "timeSlot": "09:00 - 16:00", "isClosed": False},
                {"days": "Lørdag", "timeSlot": "10:00 - 15:00", "isClosed": False},
            ],
        }

        # Uses 5 queries:
        # - 1x for getting opening hours instance.
        # - 1x for getting related time slots.
        # - 1x for getting related deviations.
        # - 1x for getting deviation time slots
        # - 1x for getting deviation template site message and location.
        with django_assert_max_num_queries(5):
            deviation_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/opening-hours/"
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

        site_message_1 = create_site_message(
            show_message_at=timezone.now(),
            show_message_to=timezone.now() + timedelta(minutes=10),
        )
        site_message_2 = create_site_message(
            show_message_at=timezone.now(),
            show_message_to=timezone.now() + timedelta(minutes=15),
        )
        # Expired message.
        create_site_message(
            show_message_at=timezone.now() - timedelta(minutes=10),
            show_message_to=timezone.now() - timedelta(minutes=5),
        )

        expected_response = [
            {
                "text": site_message_1.text,
                "messageType": site_message_1.message_type,
                "locations": ["test-location"],
                "showMessageAt": site_message_1.show_message_at.isoformat(),
                "showMessageTo": site_message_1.show_message_to.isoformat(),
            },
            {
                "text": site_message_2.text,
                "messageType": site_message_2.message_type,
                "locations": ["test-location"],
                "showMessageAt": site_message_2.show_message_at.isoformat(),
                "showMessageTo": site_message_2.show_message_to.isoformat(),
            },
        ]

        # Uses 2 queries:
        # - 1x for getting active site messages.
        # - 1x for getting related site message locations.
        with django_assert_max_num_queries(2):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/site-messages/active/"
            )

            actual_response = json.loads(response.content)

            assert response.status_code == 200
            assert actual_response == expected_response
