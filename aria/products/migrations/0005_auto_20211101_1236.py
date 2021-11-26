# Generated by Django 3.0.7 on 2021-11-01 11:36

import aria.core.fields
import aria.core.utils
import datetime
from django.db import migrations, models
import django.db.models.manager
from django.utils.timezone import utc
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20211026_2056'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productsitestate',
            options={'verbose_name': 'Product site state', 'verbose_name_plural': 'Product site states'},
        ),
        migrations.AlterModelManagers(
            name='productfile',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='productfile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 11, 1, 11, 36, 16, 199536, tzinfo=utc), verbose_name='created time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productfile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='modified time'),
        ),
        migrations.AddField(
            model_name='productsitestate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 11, 1, 11, 36, 21, 188127, tzinfo=utc), verbose_name='created time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productsitestate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='modified time'),
        ),
        migrations.AlterField(
            model_name='product',
            name='applications',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('ceiling', 'Tak'), ('floor', 'Gulv'), ('table', 'Bord'), ('outdoors', 'Utendørs'), ('sink', 'Vask'), ('walls', 'Vegger')], max_length=50), help_text='Area of product usage. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created time'),
        ),
        migrations.AlterField(
            model_name='product',
            name='materials',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('ceramic', 'Keramikk'), ('metal', 'Metall'), ('porcelain', 'Porselen'), ('wood', 'Tre')], max_length=50), help_text='Material product is made of. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='product',
            name='styles',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('classic', 'Klassisk'), ('concrete', 'Betong'), ('luxurious', 'Luksus'), ('marble', 'Marmor'), ('natural', 'Naturlig'), ('scandinavian', 'Skandinavisk'), ('structured', 'Strukturert')], max_length=50), help_text='Which style the product line represent. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='modified time'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='additional_cost',
            field=models.FloatField(default=0.0, verbose_name='Additional cost'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='thumbnail',
            field=imagekit.models.fields.ProcessedImageField(blank=True, default='media/products/default.jpg', help_text='Image must be above 380x575px', null=True, upload_to=aria.core.utils.get_static_asset_upload_path),
        ),
    ]