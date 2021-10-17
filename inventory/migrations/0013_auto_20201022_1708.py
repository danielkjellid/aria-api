# Generated by Django 3.0.7 on 2020-10-22 15:08

from django.db import migrations, models
import imagekit.models.fields
import inventory.models.product


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20201022_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfile',
            name='file',
            field=models.FileField(upload_to='some/product/file/path', verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='some/product/image/path', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='thumbnail',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='some/product/variant/file/path'),
        ),
    ]
