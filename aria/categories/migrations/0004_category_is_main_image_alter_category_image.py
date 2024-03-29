# Generated by Django 4.1.2 on 2022-12-05 14:35

import aria.files.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0003_alter_category_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="is_main_image",
            field=models.BooleanField(
                default=False,
                help_text="The image we display first in a series of related images. Should only apply to one of the images in relation.",
                verbose_name="Is main image",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=aria.files.utils.asset_get_static_upload_path,
                verbose_name="Image",
            ),
        ),
    ]
