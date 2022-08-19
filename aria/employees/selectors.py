from aria.core.decorators import cached
from aria.employees.models import EmployeeInfo
from aria.employees.records import EmployeeInfoRecord


def employees_active_list() -> list[EmployeeInfoRecord]:
    """
    Get a list of employees associated with a certain site.
    """

    employees = (
        EmployeeInfo.objects.filter(
            is_active=True,
            display_in_team_section=True,
        )
        .select_related("user")
        .order_by("id")
    )

    return [
        EmployeeInfoRecord(
            id=employee.id,
            user_id=employee.user_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            full_name=employee.full_name,
            company_email=employee.company_email,
            profile_picture=employee.profile_picture.url
            if employee.profile_picture
            else None,
            offers_appointments=employee.offers_appointments,
            display_in_team_section=employee.display_in_team_section,
            is_active=employee.is_active,
        )
        for employee in employees
    ]


def _employees_active_list_cache_key() -> str:
    return "employees.employee_list"


@cached(key=_employees_active_list_cache_key, timeout=24 * 60)
def employees_active_list_from_cache() -> list[EmployeeInfoRecord]:
    """
    Get a list of employees associated with a certain site from the cache.
    """

    return employees_active_list()
