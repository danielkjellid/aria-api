from aria.files.tests.utils import create_image_file
from aria.suppliers.models import Supplier


def get_or_create_supplier(
    *,
    supplier_name: str = "Example supplier",
    supplier_discount: float = 0.2,
    origin_country: str = "no",
    website_link: str = "example.com",
    is_active: bool = True,
) -> Supplier:
    """
    Test utility to create a user instance.
    """
    supplier, _ = Supplier.objects.get_or_create(
        name=supplier_name,
        defaults={
            "contact_first_name": "Ola",
            "contact_last_name": "Nordmann",
            "contact_email": "ola@example.com",
            "supplier_discount": supplier_discount,
            "website_link": website_link,
            "origin_country": origin_country,
            "is_active": is_active,
            "image": create_image_file(
                name=supplier_name, extension="JPEG", width=2048, height=1150
            ),
        },
    )

    return supplier
