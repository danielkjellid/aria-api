# Generated by Django 3.0.7 on 2021-05-30 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0046_auto_20210530_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsitestate',
            name='can_be_picked_up',
            field=models.BooleanField(default=False, help_text='Designates whether the product can be purchased and picked up in store', verbose_name='Can be picked up'),
        ),
        migrations.AddField(
            model_name='productsitestate',
            name='can_be_purchased_online',
            field=models.BooleanField(default=False, help_text='Designates whether the product can be purchased and shipped', verbose_name='Can be purchased online'),
        ),
    ]
