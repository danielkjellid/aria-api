# Generated by Django 3.2.9 on 2021-12-14 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_auto_20211128_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='circumference',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='circumference in centimeters', max_digits=6, null=True, verbose_name='circumference'),
        ),
        migrations.AlterField(
            model_name='size',
            name='depth',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='depth in centimeters', max_digits=6, null=True, verbose_name='depth'),
        ),
        migrations.AlterField(
            model_name='size',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='height in centimeters', max_digits=6, null=True, verbose_name='height'),
        ),
        migrations.AlterField(
            model_name='size',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='width in centimeters', max_digits=6, null=True, verbose_name='width'),
        ),
    ]