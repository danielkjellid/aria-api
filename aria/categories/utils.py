import os

from django.core.files.base import ContentFile
from django.db import transaction

from aria.categories.models import Category
from aria.products.models import Product
from aria.product_categorization.models import Category as ProductCategory


def copy_categories():
    with transaction.atomic():
        products = Product.objects.all()

        for product in products:
            attached_subcategories = product.category.all()
            categories_to_attach = []

            for subcategory in attached_subcategories:
                print(f"Currently working on {subcategory.slug}")
                new_structure_equivalent = Category.objects.get(slug=subcategory.slug)
                categories_to_attach.append(new_structure_equivalent)

            product.categories.set(categories_to_attach)
            product.save()

            print(f"Added categories for {product.name}")
    print("-----------------------")
    print("All categories copied.")


def copy_images():

    def _update_category_in_bluk(categories, instance):
        for category in categories:
            if category.slug == instance.slug:
                if instance.image and instance.image.name:
                    category_image = ContentFile(instance.image.read())
                    category_image.name = os.path.basename(instance.image.name)
                    category.image = category_image

                    category.save()
                    print(f"Copied images for category for {category.name}")

    product_categories = ProductCategory.objects.all()
    categories = Category.objects.all()

    with transaction.atomic():
        for product_category in product_categories:

            _update_category_in_bluk(categories=categories, instance=product_category)

            for subcategory in product_category.children.all():
                _update_category_in_bluk(categories=categories, instance=subcategory)
    print("-----------------------")
    print("All category images copied.")