# Generated by Django 4.1.1 on 2022-10-20 09:35

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_rename_new_description_product_description"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={
                "permissions": [
                    (
                        "product.view",
                        "Has access to view limited info about a product.",
                    ),
                    (
                        "product.management",
                        "Has access to manage products (add, edit, etc).",
                    ),
                    (
                        "product.admin",
                        "Has admin access to all product functionality, including all info.",
                    ),
                ],
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="product",
            name="materials",
            field=aria.core.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("kompositt", "Kompositt"),
                        ("dado kvarts", "DADOkvarts"),
                        ("rustfritt stål", "Rustfritt stål"),
                        ("pusset stål", "Pusset stål"),
                        ("metall", "Metall"),
                        ("tre", "Tre"),
                        ("laminat", "Laminat"),
                        ("glass", "Glass"),
                        ("marmor", "Marmor"),
                    ],
                    max_length=50,
                ),
                blank=True,
                help_text=(
                    "Material product is made of. Want to add more options? Reach out to Daniel.",
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="rooms",
            field=aria.core.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("badrom", "Bad"),
                        ("kjøkken", "Kjøkken"),
                        ("stue gang oppholdsrom", "Stue, gang og oppholdsrom"),
                        ("uterom", "Uterom"),
                    ],
                    max_length=50,
                ),
                blank=True,
                help_text="Rooms applicable to product.",
                null=True,
                size=None,
            ),
        ),
    ]
