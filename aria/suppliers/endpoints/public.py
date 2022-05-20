from aria.api.decorators import api
from ninja import Router
from pydantic import parse_obj_as
from aria.suppliers.schemas.outputs import SupplierListOutput
from aria.suppliers.models import Supplier
from aria.api.schemas.responses import APIResponse

router = Router(tags="suppliers")


@api(
    router,
    "/",
    method="GET",
    response={200: APIResponse},
    summary="Lists all active suppliers",
)
def supplier_list_api(request) -> tuple[int, APIResponse]:
    suppliers = list(Supplier.objects.filter(is_active=True))
    qs_to_schema = parse_obj_as(list[SupplierListOutput], suppliers)

    return 200, APIResponse(data=qs_to_schema)
