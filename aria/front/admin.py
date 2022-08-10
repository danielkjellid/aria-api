from django.contrib import admin

from aria.front.models import (
    OpeningHours,
    OpeningHoursDeviation,
    OpeningHoursDeviationTemplate,
    OpeningHoursTimeSlot,
    SiteMessage,
    SiteMessageLocation,
)


@admin.register(SiteMessage)
class SiteMessageAdmin(admin.ModelAdmin):
    list_display = ("message_type", "show_message_at", "show_message_to")
    filter_horizontal = ("locations",)


@admin.register(SiteMessageLocation)
class SiteMessageLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")


class OpeningHoursTimeSlotInline(admin.StackedInline):
    model = OpeningHoursTimeSlot


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    inlines = [OpeningHoursTimeSlotInline]


@admin.register(OpeningHoursDeviation)
class OpeningHoursDeviationAdmin(admin.ModelAdmin):
    list_display = (
        "opening_hours",
        "template",
        "active_at",
        "active_to",
        "disable_appointment_bookings",
    )
    inlines = [OpeningHoursTimeSlotInline]


@admin.register(OpeningHoursDeviationTemplate)
class OpeningHoursDeviationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name",)
