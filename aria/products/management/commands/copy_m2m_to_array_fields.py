from django.core.management.base import BaseCommand

from aria.products import enums
from aria.products.models import Product


class Command(BaseCommand):
    help = "Converts many to many models to new structure"

    def handle(self, *args, **options):

        products = Product.objects.all()

        for i, product in enumerate(products):

            print(f"Currently processing {i + 1} of {len(products)} products.")

            product_materials = product.materials.all()
            product_applications = product.applications.all()
            product_styles = product.styles.all()

            materials = self._loop_over_and_copy(
                product_materials, enums.ProductMaterials
            )
            applications = self._loop_over_and_copy(
                product_applications, enums.ProductApplications
            )
            styles = self._loop_over_and_copy(product_styles, enums.ProductStyles)

            product.temp_materials = materials
            product.temp_applications = applications
            product.temp_styles = styles

            product.save()

    def _loop_over_and_copy(self, m2m_relation, enum):
        """
        Find equal values from m2m relation in the specified enum,
        and return a list of appropriate enum instances.
        """

        results = []

        for relation in m2m_relation:
            for item in enum:
                if relation.name == item.label:
                    results.append(item)

        if len(m2m_relation) != len(results):
            raise RuntimeError(
                f"{set([relation.name for relation in m2m_relation]) - set([item.label for item in enum])} is not in the {enum} enum."
            )

        return results
