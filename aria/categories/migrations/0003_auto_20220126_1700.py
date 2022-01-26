from django.db import migrations, transaction


def backfill_from_product_categorization(apps, schema_editor):
    product_categorization_category_model = apps.get_model(
        "product_categorization", "Category"
    )
    category_model = apps.get_model("categories", "Category")

    parents_to_create = []
    children_to_create = []

    with transaction.atomic():
        for category in product_categorization_category_model.objects.all():
            category_parent = category_model(
                name=category.name,
                slug=category.slug,
                ordering=category.ordering,
                is_active=category.is_active,
                mptt_left=0,
                mptt_right=0,
                mptt_tree_id=0,
                mptt_level=0,
            )

            parents_to_create.append(category_parent)

            for subcategory in category.children.all():
                children_to_create.append(
                    category_model(
                        parent=category_parent,
                        name=subcategory.name,
                        slug=subcategory.slug,
                        ordering=subcategory.ordering,
                        is_active=subcategory.is_active,
                        mptt_left=0,
                        mptt_right=0,
                        mptt_tree_id=0,
                        mptt_level=0,
                    )
                )

        category_model.objects.bulk_create(parents_to_create)
        category_model.objects.bulk_create(children_to_create)


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("categories", "0002_alter_category_parent"),
    ]

    operations = [
        migrations.RunPython(
            backfill_from_product_categorization, reverse_code=migrations.RunPython.noop
        ),
    ]
