# Generated by Django 4.1 on 2022-08-26 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "suppliers",
            "0001_squashed_0005_alter_supplier_managers_remove_supplier_sites",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="supplier",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created time"),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="website_link",
            field=models.CharField(max_length=255),
        ),
    ]
