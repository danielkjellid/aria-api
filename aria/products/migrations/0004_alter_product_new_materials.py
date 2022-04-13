# Generated by Django 3.2.9 on 2022-02-07 22:12

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='new_materials',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('kompositt', 'Kompositt'), ('dado kvarts', 'DADOkvarts'), ('rustfritt stål', 'Rustfritt stål'), ('pusset stål', 'Pusset stål'), ('metall', 'Metall'), ('tre', 'Tre'), ('laminat', 'Laminat'), ('glass', 'Glass'), ('marmor', 'Marmor')], max_length=50), help_text='Material product is made of. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
    ]