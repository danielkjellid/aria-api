# Generated by Django 3.0.7 on 2021-11-17 17:32

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchens', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kitchen',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=core.utils.get_static_asset_upload_path, verbose_name='Image'),
        ),
    ]
