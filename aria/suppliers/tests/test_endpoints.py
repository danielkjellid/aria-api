import json
import tempfile

import pytest
from model_bakery import baker

from aria.suppliers.models import Supplier

pytestmark = pytest.mark.django_db


class TestPublicSuppliersEndpoints:

    BASE_ENDPOINT = "/api/suppliers"

    def test_anonymous_request_supplier_list(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test listing suppliers from an anonymous client returns
        a valid response.
        """

        suppliers = baker.make(Supplier, _quantity=4)

        for supplier in suppliers:
            with tempfile.NamedTemporaryFile(suffix=".jpg") as file:
                supplier.image = file.name
                supplier.save()

        suppliers[0].is_active = False
        suppliers[0].save()

        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3  # 3 out of 4 active
