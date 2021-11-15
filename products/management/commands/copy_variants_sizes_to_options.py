from django.core.management.base import BaseCommand, CommandParser
from django.utils.text import slugify
from django.db import transaction
from products.enums import ProductStatus
from products.models import Product, ProductOption, Variant
from django.core.files.base import ContentFile

class CopyException(Exception):
    """
    Exception raised to rollback transaction
    """

class Command(BaseCommand):
    help = 'Convert old models structures to new one'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='confirm',
            help="Indicates that the operation should be executed",
        )

    def handle(self, *args, **options) -> None:

        confirm = options['confirm']
        products = Product.objects.all()

        try:
            with transaction.atomic():

                if not confirm:
                    self.stdout.write('#######################')
                    self.stdout.write('###     DRY RUN     ###')
                    self.stdout.write('#######################')

                for iteration, product in enumerate(products):
                    self.stdout.write(f'Currently processing {iteration + 1} of {len(products)} products (product {product.id})')

                    product_variants = product.variants.all()
                    product_sizes = product.sizes.all()

                    for product_variant in product_variants:

                        variant_image_copy = ContentFile(product_variant.thumbnail.read())
                        variant_image_copy_name = product_variant.thumbnail.name.split("/")[-1]

                        variant = Variant.objects.create(
                            name=product_variant.name,
                            status=ProductStatus.AVAILABLE,
                        )

                        variant.thumbnail.save(f'{slugify(variant.name)}-{variant_image_copy_name}', variant_image_copy)

                        if len(list(product_sizes)) > 0:
                            for product_size in product_sizes:

                                self.stdout.write(f'Combining {variant} with {product_size.size}')
                                ProductOption.objects.create(
                                    product=product,
                                    variant=variant,
                                    size=product_size.size,
                                    gross_price=0.00
                                )
                                self.stdout.write(f'Option created.')
                        elif product.available_in_special_sizes:

                            self.stdout.write(f'Combining {variant} with special size')
                            ProductOption.objects.create(
                                product=product,
                                variant=variant,
                                size=None,
                                gross_price=0.00
                            )
                            self.stdout.write(f'Option created.')

                options_count = ProductOption.objects.all().count()

                self.stdout.write(f'Migration finished, created {options_count} options.')

                if not confirm:
                    self.stdout.write('Dry run complete.')
                    # Raise exception to cancel transaction(s)
                    raise CopyException()

        except CopyException:
            pass