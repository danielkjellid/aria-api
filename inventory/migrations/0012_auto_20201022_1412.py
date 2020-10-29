# Generated by Django 3.0.7 on 2020-10-22 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_product_search_keywords'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sizes',
            field=models.ManyToManyField(blank=True, related_name='product_size', to='inventory.ProductSize'),
        ),
    ]
