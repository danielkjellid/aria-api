# Generated by Django 3.0.7 on 2021-05-30 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('inventory', '0048_auto_20210530_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsitestate',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_site_state', to='inventory.Product'),
        ),
        migrations.AlterField(
            model_name='productsitestate',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_state', to='sites.Site'),
        ),
    ]