# Generated by Django 4.1.1 on 2022-10-22 13:16

from django.db import migrations, models

import imagekit.models.fields

import aria.files.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Color",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created time"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified time"),
                ),
                (
                    "name",
                    models.CharField(max_length=100, unique=True, verbose_name="name"),
                ),
                (
                    "color_hex",
                    models.CharField(
                        max_length=7, unique=True, verbose_name="color code"
                    ),
                ),
            ],
            options={
                "verbose_name": "Color",
                "verbose_name_plural": "Colors",
            },
        ),
        migrations.CreateModel(
            name="Shape",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created time"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified time"),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        upload_to=aria.files.utils.asset_get_static_upload_path,
                        verbose_name="Image",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=30, unique=True, verbose_name="name"),
                ),
            ],
            options={
                "verbose_name": "Shape",
                "verbose_name_plural": "Shapes",
            },
        ),
        migrations.CreateModel(
            name="Size",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created time"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified time"),
                ),
                (
                    "width",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Width in centimeters",
                        max_digits=6,
                        null=True,
                        verbose_name="width",
                    ),
                ),
                (
                    "height",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Height in centimeters",
                        max_digits=6,
                        null=True,
                        verbose_name="height",
                    ),
                ),
                (
                    "depth",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Depth in centimeters",
                        max_digits=6,
                        null=True,
                        verbose_name="depth",
                    ),
                ),
                (
                    "circumference",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Circumference in centimeters",
                        max_digits=6,
                        null=True,
                        verbose_name="circumference",
                    ),
                ),
            ],
            options={
                "verbose_name": "Size",
                "verbose_name_plural": "Sizes",
                "ordering": ["width", "height", "depth", "circumference"],
            },
        ),
        migrations.CreateModel(
            name="Variant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created time"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified time"),
                ),
                (
                    "thumbnail",
                    imagekit.models.fields.ProcessedImageField(
                        blank=True,
                        help_text="Image must be above 380x575px",
                        upload_to=aria.files.utils.asset_get_static_upload_path,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, verbose_name="product variant name"
                    ),
                ),
                (
                    "is_standard",
                    models.BooleanField(
                        default=False,
                        help_text="Designates if a variant should be treated as standard. This is to avoid multiple instances of the same variant. This field will also prevent cleanup deletion of these models.",
                        verbose_name="standard",
                    ),
                ),
            ],
            options={
                "verbose_name": "Variant",
                "verbose_name_plural": "Variants",
            },
        ),
        migrations.AddConstraint(
            model_name="size",
            constraint=models.UniqueConstraint(
                fields=("width", "height", "depth", "circumference"), name="size_unique"
            ),
        ),
    ]
