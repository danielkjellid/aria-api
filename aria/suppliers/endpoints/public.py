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
    response={200: list[SupplierListOutput]},
    summary="Lists all active suppliers",
)
def supplier_list_api(request) -> tuple[int, list[SupplierListOutput]]:
    suppliers = list(Supplier.objects.filter(is_active=True))

    return 200, suppliers
