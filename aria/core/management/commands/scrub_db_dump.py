from django.core.management.base import BaseCommand, CommandParser
from aria.core.decorators import not_in_production
from django.conf import settings
from django.db import connection, transaction
from django.utils.crypto import get_random_string
from django.contrib.sites.models import Site
from aria.users.models import User


class ScrubDbException(Exception):
    """
    Exception raised to rollback transaction
    """


@not_in_production
class Command(BaseCommand):

    help = "Scrubs production database, removing all personal data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            type=str,
            default="ariatestpassword",
            help="Password to set for all accounts",
            required=False,
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            dest="confirm",
            default=False,
            help="Indicates that the operation should be executed",
        )

    def handle(self, *args, **options):

        confirm = options["confirm"]
        password = options["password"]
        db_settings = settings.DATABASES["default"]

        try:
            with transaction.atomic():
                self.stdout.write(f"Cleaning {db_settings['NAME']} database...")

                #############
                # User data #
                #############

                self.stdout.write("Scrubbing personal data for all accounts...")

                # Only encrypt password once
                user = User.objects.first()
                user.set_password(password)
                user.save()

                # Set the password for all users once encrypted
                raw_sql = """
                    UPDATE users_user SET 
                        password = %s,
                        phone_number = case when phone_number <> '' then cast(md5(phone_number||%s) as varchar(20)) else '' end,
                        birth_date = date_trunc('year', birth_date),
                        email = case when is_staff = false then id || '@example.com' else email end,
                        first_name = case when is_staff = false then 'Firstname' else first_name end,
                        last_name = case when is_staff = false then 'Lastname' else last_name end;
                """

                random_string = get_random_string(length=20)

                cursor = connection.cursor()
                cursor.execute(raw_sql, [user.password, random_string])

                self.stdout.write("Personal data scrubbed.")

                if not confirm:
                    self.stdout.write(
                        "Dry run complete, run with --confirm to execute."
                    )
                    raise ScrubDbException()
        except ScrubDbException:
            pass
