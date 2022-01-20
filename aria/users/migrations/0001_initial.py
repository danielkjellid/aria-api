# Generated by Django 3.0.7 on 2021-03-21 12:49

import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0011_update_proxy_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="email address"),
                ),
                (
                    "first_name",
                    models.CharField(max_length=255, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=255, verbose_name="last name"),
                ),
                (
                    "avatar_color",
                    models.CharField(
                        choices=[
                            ("#F87171", "Red"),
                            ("#FBBF24", "Yellow"),
                            ("#34D399", "Green"),
                            ("#60A5FA", "Blue"),
                            ("#A78BFA", "Purple"),
                            ("#F472B6", "Pink"),
                        ],
                        max_length=8,
                        verbose_name="avatar color",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(
                        default="2020-03-11", null=True, verbose_name="birth date"
                    ),
                ),
                ("phone_number", models.CharField(max_length=30)),
                ("has_confirmed_email", models.BooleanField(default=False)),
                (
                    "street_address",
                    models.CharField(max_length=255, verbose_name="street name"),
                ),
                ("zip_code", models.CharField(max_length=20, verbose_name="zip code")),
                (
                    "zip_place",
                    models.CharField(max_length=255, verbose_name="postal place"),
                ),
                (
                    "disabled_emails",
                    models.BooleanField(
                        default=False,
                        help_text="Decides if a user receives email from us. Typically used if we do not want a user to receive marketing (competetors).",
                        verbose_name="disabled email",
                    ),
                ),
                (
                    "subscribed_to_newsletter",
                    models.BooleanField(
                        default=True,
                        help_text="Decides if a user receives marketing emails from us.",
                        verbose_name="subscribed to newsletter",
                    ),
                ),
                (
                    "allow_personalization",
                    models.BooleanField(
                        default=True,
                        help_text="Decides if a user accepts a personalized experience within the app.",
                        verbose_name="allows personalization",
                    ),
                ),
                (
                    "allow_third_party_personalization",
                    models.BooleanField(
                        default=True,
                        help_text="Decides if we share user cookies with external sources such as Facebook. This will make the user see adverts and other related content to the app.",
                        verbose_name="allows third party personalization",
                    ),
                ),
                (
                    "acquisition_source",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="acquisition source"
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts if you want to preserve the data.",
                        verbose_name="active",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user is automatically granted all permissions.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "permissions": (
                    ("has_users_list", "Can list users"),
                    ("has_user_edit", "Can edit a single user instance"),
                    ("has_user_add", "Can add a single user instance"),
                    ("has_user_delete", "Can delete a single user instance"),
                ),
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("on_site", django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
