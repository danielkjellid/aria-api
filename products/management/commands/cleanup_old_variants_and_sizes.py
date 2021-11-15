from django.core.management.base import BaseCommand, CommandParser
from django.utils.text import slugify
from django.db import transaction
from products.enums import ProductStatus
from products.models import Product, ProductOption, ProductSize, ProductVariant, Variant
from django.core.files.base import ContentFile
from django.db.models import Count

class CleanupException(Exception):
    """
    Exception raised to rollback transaction
    """

class Command(BaseCommand):
    help = 'Cleanup old models after convertion'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='confirm',
            help="Indicates that the operation should be executed",
        )

    def handle(self, *args, **options) -> None:
        confirm = options['confirm']

        try:
            with transaction.atomic():
                if not confirm:
                    self.stdout.write('#######################')
                    self.stdout.write('###     DRY RUN     ###')
                    self.stdout.write('#######################')

                product_variants = ProductVariant.objects.all()
                product_sizes = ProductSize.objects.all().distinct('size__width', 'size__height')
                variants = Variant.objects.all()
                option_sizes = ProductOption.objects.all().distinct('size__width', 'size__height')

                # Actual deletion of instances
                for iteration, product_variant in enumerate(product_variants):
                    self.stdout.write(f'Deleting variant {iteration + 1} of {len(product_variants)}')
                    product_variant.delete()

                for iteration, product_size in enumerate(product_sizes):
                    self.stdout.write(f'Deleting size {iteration + 1} of {len(product_sizes)}')
                    product_size.delete()

                if not confirm:
                    self.stdout.write('Dry run complete.')
                    # Raise exception to cancel transaction(s)
                    raise CleanupException()

        except CleanupException:
            pass
