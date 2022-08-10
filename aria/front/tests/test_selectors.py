from datetime import time, timedelta
from unittest.mock import ANY

from django.core.cache import cache
from django.utils import timezone

import pytest

from aria.front.enums import SiteMessageType
from aria.front.models import OpeningHours, SiteMessage
from aria.front.records import (
    OpeningHoursDeviationRecord,
    OpeningHoursDeviationTemplateRecord,
    OpeningHoursRecord,
    OpeningHoursTimeSlotHumanReadableRecord,
    OpeningHoursTimeSlotRecord,
    SiteMessageRecord,
)
from aria.front.selectors import (
    _opening_hours_time_slot_by_weekdays,
    _opening_hours_weekdays_by_time_slots,
    deviation_record_for_opening_hours,
    opening_hours_detail,
    opening_hours_detail_from_cache,
    opening_hours_record,
    site_message_active_list,
    site_message_active_list_from_cache,
    site_message_record,
)
from aria.front.tests.utils import (
    create_opening_hours,
    create_opening_hours_deviation,
    create_site_message,
)
from aria.front.types import WeekdaysByTimeSlotDict

pytestmark = pytest.mark.django_db


class TestFrontSelectors:
    def test_site_message_record(self, django_assert_max_num_queries) -> None:
        """
        Test the site_message_record selector returns expected response within
        query limit for a specific site message.
        """

        start_time = timezone.now()
        end_time = timezone.now() + timedelta(minutes=10)
        site_message = create_site_message(
            show_message_at=start_time, show_message_to=end_time
        )

        # Uses 1 query to get related locations.
        with django_assert_max_num_queries(1):
            sm_record = site_message_record(site_message)

        assert sm_record == SiteMessageRecord(
            id=site_message.id,
            text=site_message.text,
            message_type=SiteMessageType(site_message.message_type),
            locations=["test-location"],
            show_message_at=start_time,
            show_message_to=end_time,
        )

        site_message_with_locations = (
            SiteMessage.objects.filter(id=site_message.id).with_locations().first()
        )

        # Should use already prefetched value, and not hit DB.
        with django_assert_max_num_queries(0):
            sm_record_with_prefetch = site_message_record(site_message_with_locations)

        assert sm_record_with_prefetch == SiteMessageRecord(
            id=site_message.id,
            text=site_message.text,
            message_type=SiteMessageType(site_message.message_type),
            locations=["test-location"],
            show_message_at=start_time,
            show_message_to=end_time,
        )

    def test_site_message_active_list(self, django_assert_max_num_queries) -> None:
        """
        Test that the site_message_active_list selector returns expected output
        within query limit.
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

        # Uses 2 queries: 1 for getting site messages, and 1 for getting related
        # locations.
        with django_assert_max_num_queries(2):
            active_list = site_message_active_list()

        assert len(active_list) == 2
        assert sorted(active_list, key=lambda x: x.id) == [
            SiteMessageRecord(
                id=site_message_1.id,
                text=site_message_1.text,
                message_type=SiteMessageType(site_message_1.message_type),
                locations=["test-location"],
                show_message_at=site_message_1.show_message_at,
                show_message_to=site_message_1.show_message_to,
            ),
            SiteMessageRecord(
                id=site_message_2.id,
                text=site_message_2.text,
                message_type=SiteMessageType(site_message_2.message_type),
                locations=["test-location"],
                show_message_at=site_message_2.show_message_at,
                show_message_to=site_message_2.show_message_to,
            ),
        ]

    def test_site_message_active_list_from_cache(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the site_message_active_list_from_cache correctly returns from
        cache, and output is as expected, within query limits.
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

        cache.delete("front.site_messages")
        assert "front.site_messages" not in cache

        # Uses 2 queries: 1 for getting site messages, and 1 for getting related
        # locations.
        with django_assert_max_num_queries(2):
            site_message_active_list_from_cache()

        # After first hit, instance should have been added to cache.
        assert "front.site_messages" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(0):
            site_message_active_list_from_cache()

        assert cache.get("front.site_messages") == [
            {
                "id": site_message_1.id,
                "text": site_message_1.text,
                "message_type": site_message_1.message_type,
                "locations": ["test-location"],
                "show_message_at": site_message_1.show_message_at,
                "show_message_to": site_message_1.show_message_to,
            },
            {
                "id": site_message_2.id,
                "text": site_message_2.text,
                "message_type": site_message_2.message_type,
                "locations": ["test-location"],
                "show_message_at": site_message_2.show_message_at,
                "show_message_to": site_message_2.show_message_to,
            },
        ]

    def test__opening_hours_weekdays_by_time_slots(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the _opening_hours_weekdays_by_time_slot selector returns
        expected output given a certain scenario.
        """

        opening_hours = create_opening_hours()
        opening_hours_time_slots = list(opening_hours.time_slots.all())

        expected_output = [
            WeekdaysByTimeSlotDict(
                time_slot="09:00 - 17:00",
                days=["Mandag", "Tirsdag", "Onsdag", "Torsdag"],
                is_closed=False,
            ),
            WeekdaysByTimeSlotDict(
                time_slot="09:00 - 16:00",
                days=["Fredag"],
                is_closed=False,
            ),
            WeekdaysByTimeSlotDict(
                time_slot="10:00 - 15:00",
                days=["Lørdag"],
                is_closed=False,
            ),
            WeekdaysByTimeSlotDict(
                time_slot=None,
                days=["Søndag"],
                is_closed=True,
            ),
        ]

        with django_assert_max_num_queries(0):
            weekdays_by_time_slots = _opening_hours_weekdays_by_time_slots(
                time_slots=opening_hours_time_slots
            )

        assert weekdays_by_time_slots == expected_output

    def test__opening_hours_time_slot_by_weekdays(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the _opening_hours_time_slot_by_weekdays selector returns
        expected output given a certain scenario.
        """

        opening_hours = create_opening_hours()
        opening_hours_time_slots = list(opening_hours.time_slots.all())

        expected_output = [
            OpeningHoursTimeSlotHumanReadableRecord(
                days="Mandag - Torsdag", time_slot="09:00 - 17:00", is_closed=False
            ),
            OpeningHoursTimeSlotHumanReadableRecord(
                days="Fredag", time_slot="09:00 - 16:00", is_closed=False
            ),
            OpeningHoursTimeSlotHumanReadableRecord(
                days="Lørdag", time_slot="10:00 - 15:00", is_closed=False
            ),
            OpeningHoursTimeSlotHumanReadableRecord(
                days="Søndag", time_slot=None, is_closed=True
            ),
        ]

        weekdays_by_time_slots = _opening_hours_weekdays_by_time_slots(
            time_slots=opening_hours_time_slots
        )

        with django_assert_max_num_queries(0):
            time_slot_by_weekdays = _opening_hours_time_slot_by_weekdays(
                weekdays_by_time_slots=weekdays_by_time_slots
            )

        assert time_slot_by_weekdays == expected_output

    def test_opening_hours(self, django_assert_max_num_queries) -> None:
        """
        Test that the opening_hours selector returns
        expected output both normally and with an active deviation.
        """

        opening_hours = create_opening_hours()

        # Uses 3 queries:
        # - 1x for getting opening hour instance
        # - 1x for getting time slots
        # - 1x for getting deviations
        with django_assert_max_num_queries(3):
            oh_record_for_site = opening_hours_detail()

        assert oh_record_for_site == OpeningHoursRecord(
            id=opening_hours.id,
            time_slots=[
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="monday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="tuesday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="wednesday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="thursday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="friday",
                    opening_at=time(9, 0),
                    closing_at=time(16, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="saturday",
                    opening_at=time(10, 0),
                    closing_at=time(15, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="sunday",
                    opening_at=None,
                    closing_at=None,
                    is_closed=True,
                ),
            ],
            human_readable_time_slots=[
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Mandag - Torsdag", time_slot="09:00 - 17:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Fredag", time_slot="09:00 - 16:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Lørdag", time_slot="10:00 - 15:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Søndag", time_slot=None, is_closed=True
                ),
            ],
        )

        # Create a deviation to override output
        create_opening_hours_deviation(
            opening_hours_id=opening_hours.id,
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 5 queries:
        # - 1x for getting opening hour instance.
        # - 1x for getting time slots.
        # - 1x for getting deviations.
        # - 1x for getting time slots for deviation.
        # - 1x for getting site_message and location for deviation.
        with django_assert_max_num_queries(5):
            oh_record_with_active_deviation_for_site = opening_hours_detail()

        assert oh_record_with_active_deviation_for_site == OpeningHoursRecord(
            id=opening_hours.id,
            time_slots=[
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="monday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="tuesday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="wednesday",
                    opening_at=None,
                    closing_at=None,
                    is_closed=True,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="thursday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="friday",
                    opening_at=time(9, 0),
                    closing_at=time(16, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="saturday",
                    opening_at=time(10, 0),
                    closing_at=time(15, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="sunday",
                    opening_at=None,
                    closing_at=None,
                    is_closed=True,
                ),
            ],
            human_readable_time_slots=[
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Mandag, Tirsdag og Torsdag",
                    time_slot="09:00 - 17:00",
                    is_closed=False,
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Onsdag og Søndag", time_slot=None, is_closed=True
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Fredag", time_slot="09:00 - 16:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Lørdag", time_slot="10:00 - 15:00", is_closed=False
                ),
            ],
        )

    def test_opening_hours_for_site_from_cache(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the opening_hours_for_site_from_cache correctly returnes from
        cache, and output is as expected.
        """

        opening_hours = create_opening_hours()

        # Make sure we're in a healthy state before continuing.
        cache.delete("front.opening_hours")
        assert "front.opening_hours" not in cache

        # Uses 3 queries:
        # - 1x for getting opening hour instance
        # - 1x for getting time slots
        # - 1x for getting deviations
        with django_assert_max_num_queries(3):
            opening_hours_detail_from_cache()

        # After first hit, instance should have been added to cache.
        assert "front.opening_hours" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(0):
            opening_hours_detail_from_cache()

        # Assert that the object in cache is as expected.
        assert cache.get("front.opening_hours") == {
            "id": opening_hours.id,
            "time_slots": [
                {
                    "id": ANY,
                    "weekday": "monday",
                    "opening_at": time(9, 0),
                    "closing_at": time(17, 0),
                    "is_closed": False,
                },
                {
                    "id": ANY,
                    "weekday": "tuesday",
                    "opening_at": time(9, 0),
                    "closing_at": time(17, 0),
                    "is_closed": False,
                },
                {
                    "id": ANY,
                    "weekday": "wednesday",
                    "opening_at": time(9, 0),
                    "closing_at": time(17, 0),
                    "is_closed": False,
                },
                {
                    "id": ANY,
                    "weekday": "thursday",
                    "opening_at": time(9, 0),
                    "closing_at": time(17, 0),
                    "is_closed": False,
                },
                {
                    "id": ANY,
                    "weekday": "friday",
                    "opening_at": time(9, 0),
                    "closing_at": time(16, 0),
                    "is_closed": False,
                },
                {
                    "id": ANY,
                    "weekday": "saturday",
                    "opening_at": time(10, 0),
                    "closing_at": time(15, 0),
                    "is_closed": False,
                },
                {
                    "id": ANY,
                    "weekday": "sunday",
                    "opening_at": None,
                    "closing_at": None,
                    "is_closed": True,
                },
            ],
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

    def test_opening_hours_record(self, django_assert_max_num_queries) -> None:
        """
        Test the opening_hours_record selector returns expected response
        within query limit for a specific category.
        """

        opening_hours = create_opening_hours()

        expected_output = OpeningHoursRecord(
            id=opening_hours.id,
            time_slots=[
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="monday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="tuesday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="wednesday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="thursday",
                    opening_at=time(9, 0),
                    closing_at=time(17, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="friday",
                    opening_at=time(9, 0),
                    closing_at=time(16, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="saturday",
                    opening_at=time(10, 0),
                    closing_at=time(15, 0),
                    is_closed=False,
                ),
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="sunday",
                    opening_at=None,
                    closing_at=None,
                    is_closed=True,
                ),
            ],
            human_readable_time_slots=[
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Mandag - Torsdag", time_slot="09:00 - 17:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Fredag", time_slot="09:00 - 16:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Lørdag", time_slot="10:00 - 15:00", is_closed=False
                ),
                OpeningHoursTimeSlotHumanReadableRecord(
                    days="Søndag", time_slot=None, is_closed=True
                ),
            ],
        )

        # Uses 1 query to get associated time_slots.
        with django_assert_max_num_queries(1):
            oh_record = opening_hours_record(opening_hours=opening_hours)

        assert oh_record == expected_output

    def test_deviation_record_for_opening_hours(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test the deviation_record_for_opening_hours selector returns expected response
        within query limit for a specific category.
        """

        opening_hours = create_opening_hours()
        active_deviation = create_opening_hours_deviation(
            opening_hours_id=opening_hours.id,
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        expected_output = OpeningHoursDeviationRecord(
            id=active_deviation.id,
            opening_hours_id=opening_hours.id,
            template=OpeningHoursDeviationTemplateRecord(
                id=active_deviation.template.id,
                name=active_deviation.template.name,
                description=active_deviation.template.description,
                site_message=SiteMessageRecord(
                    id=active_deviation.template.site_message.id,
                    text=active_deviation.template.site_message.text,
                    message_type=active_deviation.template.site_message.message_type,
                    locations=[
                        location.slug
                        for location in active_deviation.template.site_message.locations.all()  # pylint: disable=line-too-long
                    ],
                    show_message_at=active_deviation.template.site_message.show_message_at,  # pylint: disable=line-too-long
                    show_message_to=active_deviation.template.site_message.show_message_to,  # pylint: disable=line-too-long
                )
                if active_deviation.template.site_message
                else None,
            ),
            active_at=active_deviation.active_at,
            active_to=active_deviation.active_to,
            description=active_deviation.description,
            disable_appointment_bookings=active_deviation.disable_appointment_bookings,
            time_slots=[
                OpeningHoursTimeSlotRecord.construct(
                    id=ANY,
                    weekday="wednesday",
                    opening_at=None,
                    closing_at=None,
                    is_closed=True,
                )
            ],
        )

        # Uses 3 queries:
        # - 1x for getting opening hours' related deviation
        # - 1x for getting deviation time slots
        # - 1x for getting deviation template site message
        with django_assert_max_num_queries(3):
            deviation_record = deviation_record_for_opening_hours(
                opening_hours=opening_hours
            )

        assert deviation_record == expected_output

        prefetched_opening_hours = (
            OpeningHours.objects.filter(id=opening_hours.id)
            .with_active_deviations()
            .first()
        )

        # Uses 0 queries since all values needed is already prefetched.
        with django_assert_max_num_queries(0):
            prefetched_deviation_record = deviation_record_for_opening_hours(
                opening_hours=prefetched_opening_hours
            )

        assert prefetched_deviation_record == expected_output
