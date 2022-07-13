# Generated by Django 4.0.5 on 2022-07-08 16:52

import aria.kitchens.models
from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('kitchens', '0003_remove_decor_thumbnail_remove_plywood_thumbnail_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decor',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=aria.kitchens.models.Decor.kitchen_decor_upload_path),
        ),
        migrations.AlterField(
            model_name='plywood',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=aria.kitchens.models.Plywood.kitchen_plywood_upload_path),
        ),
    ]