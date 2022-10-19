from django.http import HttpRequest

from ninja import Router, Schema

from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.suppliers.models import Supplier

router = Router(tags=["Suppliers"])


class SupplierListInternalOutput(Schema):
    id: int
    name: str
    is_active: bool


@router.get(
    "/",
    response={200: list[SupplierListInternalOutput], codes_40x: ExceptionResponse},
    summary="List all suppliers.",
    url_name="internal-suppliers-index",  # Temporary.
)
def supplier_list_internal_api(
    request: HttpRequest,
) -> list[SupplierListInternalOutput]:
    """
    Endpoint for getting a list of all suppliers in the application.
    """

    suppliers = Supplier.objects.all().order_by("name")

    return [SupplierListInternalOutput.from_orm(supplier) for supplier in suppliers]
