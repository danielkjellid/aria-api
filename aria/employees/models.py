from typing import Iterable

from django.core.cache import cache
from django.db import models

from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFill

from aria.employees.managers import EmployeeInfoQuerySet

_EmployeeInfoManager = models.Manager.from_queryset(EmployeeInfoQuerySet)


class EmployeeInfo(models.Model):
    """
    Stores different employee information, which is related to branding, bookings
    etc.
    """

    user = models.OneToOneField(
        "users.User",
        verbose_name="user",
        null=True,
        blank=True,
        related_name="employee_info",
        on_delete=models.CASCADE,
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_email = models.EmailField()
    profile_picture = ProcessedImageField(
        upload_to="media/employees/",
        processors=[ResizeToFill(540, 540)],
        format="JPEG",
        options={"quality": 100},
        blank=True,
        null=True,
    )

    offers_appointments = models.BooleanField(
        default=False, help_text="Enables appointment booking for employee"
    )
    display_in_team_section = models.BooleanField(
        default=True, help_text="Display employee under 'Our team' frontend"
    )
    is_active = models.BooleanField(
        default=True, help_text="Designates if this is a current employee"
    )

    objects = _EmployeeInfoManager()

    class Meta:
        verbose_name = "employee info"
        verbose_name_plural = "employee info"

    def __str__(self) -> str:
        return (
            f"{self.first_name} {self.last_name}"
            if self.first_name and self.last_name
            else self.company_email
        )

    @property
    def full_name(self) -> str:
        """
        Get the full name representation of an employee
        """
        return f"{self.first_name} {self.last_name}"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        """
        Uncache employees list upon save.
        """

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if self.user and self.user.site_id:
            cache.delete(f"employees.employee_list.site_id={self.user.site_id}")
