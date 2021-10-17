# Generated by Django 3.0.7 on 2020-10-01 12:44

from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields
import inventory.models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_productimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=imagekit.models.fields.ProcessedImageField(blank=True, default='media/products/default.jpg', null=True, upload_to='some/product/path'),
        ),
        migrations.CreateModel(
            name='ProductFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Product file name')),
                ('upload', models.FileField(upload_to='media/products/files', verbose_name='File')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='inventory.Product')),
            ],
        ),
    ]
