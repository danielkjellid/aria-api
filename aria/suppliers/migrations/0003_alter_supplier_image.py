# Generated by Django 3.2.12 on 2022-05-07 20:02

import aria.core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0002_auto_20220225_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='image',
            field=models.ImageField(blank=True, upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image'),
        ),
    ]
