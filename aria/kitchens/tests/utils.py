from django.utils.text import slugify

from aria.kitchens.models import Kitchen
from aria.products.enums import ProductStatus
from aria.suppliers.models import Supplier
from aria.suppliers.tests.utils import get_or_create_supplier


def create_kitchen(
    *,
    name: str = "Test kitchen",
    slug: str | None = None,
    status: ProductStatus = ProductStatus.AVAILABLE,
    supplier: Supplier | None = None,
    can_be_painted: bool = True,
) -> Kitchen:
    """
    Test utiltiy to create a kitchen instance.
    """

    # Validate that provided slug is unique.
    if slug is not None:
        assert not Kitchen.objects.filter(slug=slug).exists()

    if supplier is None:
        supplier = get_or_create_supplier()

    kitchen = Kitchen.objects.create(
        name=name,
        supplier=supplier,
        status=status,
        slug=slug or slugify(name),
        thumbnail_description="Thumbnail desc",
        description="Desc",
        extra_description="Extra desc",
        example_from_price=40000.00,
        can_be_painted=can_be_painted,
    )

    return kitchen
