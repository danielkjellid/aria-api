from aria.products.models import Product
from aria.categories.models import Category
from django.db import transaction


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
