from aria.core.records import SiteRecord
from aria.employees.models import EmployeeInfo
from aria.employees.records import EmployeeInfoRecord


def employees_list_for_site(site_id: int) -> list[EmployeeInfoRecord]:
    """
    Get a list of employees associated with a certain site.
    """

    employees = EmployeeInfo.objects.filter(
        site_id=site_id, display_in_team_section=True
    ).select_related("user", "site")

    return [
        EmployeeInfoRecord(
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
            site=SiteRecord(
                domain=employee.site.domain,
                name=employee.site.name,
            ),
        )
        for employee in employees
    ]
