from django.http import HttpRequest
from ninja import Router

from aria.suppliers.models import Supplier
from aria.suppliers.schemas.outputs import SupplierListOutput

router = Router(tags=["Suppliers"])


@router.get(
    "/", response={200: list[SupplierListOutput]}, summary="Lists all active suppliers"
)
def supplier_list_api(request: HttpRequest) -> tuple[int, list[SupplierListOutput]]:
    """
    Endpoint for listing all active suppliers.
    """
    suppliers = Supplier.objects.filter(is_active=True)

    return 200, [SupplierListOutput.from_orm(supplier) for supplier in suppliers]
