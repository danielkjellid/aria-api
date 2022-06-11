from django.http import HttpRequest

from ninja import Router

from aria.api.decorators import api
from aria.suppliers.models import Supplier
from aria.suppliers.schemas.outputs import SupplierListOutput

router = Router(tags=["Suppliers"])


@api(
    router,
    "/",
    method="GET",
    response={200: list[SupplierListOutput]},
    summary="Lists all active suppliers",
)
def supplier_list_api(request: HttpRequest) -> tuple[int, list[SupplierListOutput]]:
    suppliers = Supplier.objects.filter(is_active=True)  # type: ignore

    return 200, [SupplierListOutput.from_orm(supplier) for supplier in suppliers]
