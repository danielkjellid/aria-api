from ninja import Router

from aria.api.decorators import api
from aria.employees.schemas.outputs import EmployeeListOutput
from aria.employees.selectors import employees_list_for_site

router = Router(tags=["Employees"])
from django.http.request import HttpRequest


@api(
    router,
    "employees/{site_id}/",
    method="GET",
    response={200: list[EmployeeListOutput]},
    summary="Get employees for a site",
)
def employee_list_api(request: HttpRequest, site_id: int) -> list[EmployeeListOutput]:
    """
    Endpoint for listing team employees related to site.
    """

    employees = employees_list_for_site(site_id=site_id)

    return [EmployeeListOutput(**employee.dict()) for employee in employees]
