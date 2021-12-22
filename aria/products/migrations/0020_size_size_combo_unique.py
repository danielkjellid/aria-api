# Generated by Django 3.2.9 on 2021-12-14 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_auto_20211214_2218'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='size',
            constraint=models.UniqueConstraint(fields=('width', 'height', 'depth', 'circumference'), name='size_combo_unique'),
        ),
    ]