from django.http.request import HttpRequest
from ninja import Router

from aria.employees.schemas.outputs import EmployeeListOutput
from aria.employees.selectors import employees_active_list_from_cache

router = Router(tags=["Employees"])


@router.get(
    "/", response={200: list[EmployeeListOutput]}, summary="Get employees for a site"
)
def employee_list_api(request: HttpRequest) -> list[EmployeeListOutput]:
    """
    Endpoint for listing team employees related to site.
    """

    employees = employees_active_list_from_cache()

    return [EmployeeListOutput(**employee.dict()) for employee in employees]
