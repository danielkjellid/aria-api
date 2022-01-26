# Generated by Django 3.2.11 on 2022-01-26 21:38

from django.db import migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_auto_20220126_1700'),
        ('products', '0002_alter_product_new_materials'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='categories',
            field=mptt.fields.TreeManyToManyField(related_name='products', to='categories.Category'),
        ),
    ]
