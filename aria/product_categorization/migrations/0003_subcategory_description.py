# Generated by Django 4.0.1 on 2022-02-04 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_categorization', '0002_subcategory_apply_filter_subcategory_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]