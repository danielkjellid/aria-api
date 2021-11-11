from django.core.management.base import BaseCommand, CommandParser
from django.utils.text import slugify
from django.db import transaction
from products.enums import ProductStatus
from products.models import Product, ProductOption, ProductSize, ProductVariant, Variant
from django.core.files.base import ContentFile

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
                product_sizes = ProductSize.objects.values('size').distinct()
                variants = Variant.objects.all()
                option_sizes = ProductOption.objects.values('size').distinct()

                # Sanity checks
                if variants.count() != product_variants.count() or list(variants) != list(product_variants):
                    raise RuntimeError('Variant and ProductVariant mismatch.')

                if option_sizes.count() != product_sizes.count() or list(option_sizes) != list(product_sizes):
                    raise RuntimeError('ProductOption size and ProductSize mismatch.')

                # Actual deletion of instances
                for product_variant in product_variants:
                    product_variant.delete()

                for product_size in product_sizes:
                    product_size.delete()

                if not confirm:
                    self.stdout.write('Dry run complete.')
                    # Raise exception to cancel transaction(s)
                    raise CleanupException()

        except CleanupException:
            pass
