# Generated by Django 3.0.7 on 2021-05-29 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0042_productsitestate'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductSiteState',
        ),
    ]