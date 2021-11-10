# Generated by Django 3.0.7 on 2021-11-10 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20211102_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='short_description',
            field=models.TextField(help_text='The short description will be displayed on the top part of the product, above the variant selection', null=True, verbose_name='Short Description'),
        ),
    ]
