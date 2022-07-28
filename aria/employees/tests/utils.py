from aria.employees.models import EmployeeInfo
from aria.users.models import User


def create_employee_info(
    *,
    user: User,
    company_email: str = "example@company.com",
    offers_appointments: bool = True,
    display_in_team_section: bool = True,
    is_active: bool = True,
) -> EmployeeInfo:

    employee, _created = EmployeeInfo.objects.update_or_create(
        user=user,
        defaults={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company_email": company_email,
            "offers_appointments": offers_appointments,
            "display_in_team_section": display_in_team_section,
            "is_active": is_active,
        },
    )

    return employee
