# Generated by Django 3.2.12 on 2022-05-07 20:02

import aria.core.utils
from django.db import migrations, models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20220427_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=imagekit.models.fields.ProcessedImageField(blank=True, help_text='Image must be above 380x575px', upload_to=aria.core.utils.get_static_asset_upload_path),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(blank=True, upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='shape',
            name='image',
            field=models.ImageField(blank=True, upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='thumbnail',
            field=imagekit.models.fields.ProcessedImageField(blank=True, help_text='Image must be above 380x575px', upload_to=aria.core.utils.get_static_asset_upload_path),
        ),
    ]
