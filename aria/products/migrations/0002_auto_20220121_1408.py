# Generated by Django 3.2.11 on 2022-01-21 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="product",
            managers=[],
        ),
        migrations.AddField(
            model_name="product",
            name="can_be_picked_up",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the product can be purchased and picked up in store",
                verbose_name="Can be picked up",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="can_be_purchased_online",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the product can be purchased and shipped",
                verbose_name="Can be purchased online",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="display_price",
            field=models.BooleanField(
                default=True,
                help_text="Designates whether the product price is displayed",
                verbose_name="Display price to customer",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="supplier_purchase_price",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=10,
                verbose_name="Supplier purchase price",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="supplier_shipping_cost",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=10,
                verbose_name="Shipping cost",
            ),
        ),
    ]