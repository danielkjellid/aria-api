import pytest
from model_bakery import baker

from aria.suppliers.models import Supplier

pytestmark = pytest.mark.django_db


class TestSuppliersModels:
    def test_supplier_model_create(self):
        """
        Test creation of supplier instances.
        """

        options = {
            "name": "Supplier",
            "contact_first_name": "User",
            "contact_last_name": "Lastname",
            "contact_email": "user@example.com",
            "supplier_discount": 0.00,
            "origin_country": "Italy",
            "is_active": True,
        }

        supplier = Supplier.objects.create(**options)

        assert supplier.name == "Supplier"
        assert supplier.contact_first_name == "User"
        assert supplier.contact_last_name == "Lastname"
        assert supplier.contact_email == "user@example.com"
        assert supplier.supplier_discount == 0.00
        assert supplier.origin_country == "Italy"
        assert supplier.is_active == True
