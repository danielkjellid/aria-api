from aria.categories.models import Category


def create_category(
    name: str = "Furniture", parent: Category | None = None
) -> Category:
    """
    Creates a dummy category for test usage
    """

    category: Category
    category, created = Category.objects.get_or_create(
        name=name, slug=name.lower().replace(" ", "-"), is_active=True
    )

    if created:
        category.ordering = Category.objects.count() + 1
        category.save(update_fields=["ordering"])

    if parent is not None:
        category.parent = parent
        category.save(update_fields=["parent"])

    return category
