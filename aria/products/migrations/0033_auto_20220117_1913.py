# Generated by Django 3.2.9 on 2022-01-17 18:13

import aria.core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0032_auto_20220117_1838'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shape',
            options={'verbose_name': 'Shape', 'verbose_name_plural': 'Shapes'},
        ),
        migrations.AddField(
            model_name='shape',
            name='image',
            field=models.ImageField(blank=True, default='media/front/default_2048x1150.jpeg', upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image'),
        ),
    ]