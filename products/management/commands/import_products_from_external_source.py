import requests
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils.text import slugify
from products.enums import ProductStatus
from suppliers.models import Supplier
from products.models import Product, ProductFile, ProductSiteState, ProductSize, ProductVariant, Size
from tempfile import NamedTemporaryFile

class ProductImportException(Exception):
    """
    Exception raised to rollback transaction
    """

class Command(BaseCommand):
    help = 'Imports products form a given JSON source'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--supplier_id',
            type=int,
            default=None,
            help='Which supplier does the products bellong to?',
            required=True
        )
        parser.add_argument(
            '--source',
            type=str,
            default=None,
            help='Source of which to get the products from',
            required=True
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='confirm',
            help="Indicates that the operation should be executed",
        )

    def handle(self, *args, **options) -> None:
        # Get given parameteres
        supplier_id = options['supplier_id']
        source = options['source']
        confirm = options['confirm']

        # A list of required keys, used in sanity check before object
        # creation.
        required_keys = ['collection_name', 'description_nor', 'sizes', 'variants', 'files']

        # Get data from source and load it as json
        products_data_url = requests.get(source)
        products_data = products_data_url.json()

        # Common variables for all products in job
        supplier = Supplier.objects.get(id=supplier_id)
        site = Site.objects.get(pk=1)

        try:
            # Wrap entire process in transaction block, that way, if there
            # are errors, it cancelles the entire operation.
            with transaction.atomic():

                if not confirm:
                    self.stdout.write('#######################')
                    self.stdout.write('###     DRY RUN     ###')
                    self.stdout.write('#######################')

                # Start loop and creation of products
                for iteration, product in enumerate(products_data):

                    self.stdout.write(f'Currently processing {iteration + 1} of {len(products_data)} products')

                    # Sanity check to check that all necessary
                    # keys are present.
                    for required_key in required_keys:
                        assert required_key in product.keys()

                    # Store local variables fetched from data source
                    product_name = product.get('collection_name')
                    short_description = product.get("short_description_nor")
                    description = product.get("description_nor")
                    sizes = product.get('sizes')
                    variants = product.get('variants')
                    files = product.get('files')

                    # This variable is determined if there is an
                    # asterix present in the sizes string
                    special_size = False

                    # Convert sizes from list to string, splitting on ","
                    # and removing whitespace
                    sizes_list = [size.strip() for size in sizes.split(',')]

                    # Handle if product comes in special sizes
                    if '*' in sizes_list:
                        special_size = True
                        sizes_list.remove('*')

                    # Reiterate over the array and split variables by delimiter
                    # return it as a list of dicts with keys height and width.
                    sizes_dict_list = self._split_and_convert_sizes(sizes_list)

                    # Create product instance
                    self.stdout.write(f'Creating product {iteration + 1}...')
                    created_product = Product.object.create(
                        name=product_name,
                        supplier=supplier,
                        status=ProductStatus.DRAFT,
                        slug=slugify(product_name),
                        short_description=short_description,
                        description=description,
                        available_in_special_sizes=special_size,
                        is_imported_from_external_source=True,
                    )
                    self.stdout.write(f'Product {created_product.name} created.')

                    # Add site to m2m rel.
                    self.stdout.write('Adding active site to product...')
                    created_product.sites.add(site)
                    created_product.save()
                    self.stdout.write('Active site added.')

                    # Create site state for m2m rel.
                    self.stdout.write('Creating site state...')
                    ProductSiteState.object.create(
                        site=site,
                        product=created_product,
                        gross_price=0.0,
                        display_price=False,
                        can_be_purchased_online=False,
                        can_be_picked_up=False,
                        supplier_purchase_price=0.0,
                        supplier_shipping_cost=0.0
                    )
                    self.stdout.write('Site state created.')

                    # Create variants instances
                    self.stdout.write('Creating variants...')
                    for variant in variants:
                        ProductVariant.objects.create(
                            product=created_product,
                            name=variant['name'],
                            status=ProductStatus.AVAILABLE,
                            thumbnail=self._get_remote_asset(variant['image_url'], variant['name']),
                            additional_cost=0.0
                        )
                        self.stdout.write(f'Variant {variant["name"]} added.')
                    self.stdout.write('All variants created.')

                    # Create files instances
                    self.stdout.write('Creating files...')
                    for file in files:
                        name: str
                        value: str

                        for key, value in file.items():
                            if key == 'technical_sheet_url':
                                name = 'Spesifikasjoner'
                            elif key == 'laying_system_url':
                                name = 'Leggingsmønster'
                            elif key == 'dop_certification_url':
                                name = 'Sertifisering'
                            elif key == 'environment_certification_url':
                                name = 'Miljøsertifisering'
                            elif key == 'k2_catalog_url':
                                name = 'K2 Katalog'
                            else:
                                name = 'Katalog'

                            value = value

                        ProductFile.object.create(
                            product=created_product,
                            name=name,
                            file=self._get_remote_asset(value, name)
                        )
                        self.stdout.write(f'File {name} added.')
                    self.stdout.write('All files created.')

                    # Create sizes instances
                    self.stdout.write('Getting and creating appropriate sizes...')
                    sizes_to_link = []

                    for size_set in sizes_dict_list:
                        height = size_set.get('height')
                        width = size_set.get('width')

                        size = Size.objects.get_or_create(
                            width=width,
                            height=height
                        )

                        sizes_to_link.append(size)
                    self.stdout.write('All sizes fetched and ready to link.')

                    # Relate sizes to product
                    self.stdout.write('Linking sizes to product...')
                    for size, created in sizes_to_link:
                        ProductSize.objects.create(
                            product=created_product,
                            size=size,
                            additional_cost=0.0
                        )
                    self.stdout.write('All sizes linked.')
                    self.stdout.write('----------------------------------------------')

                if not confirm:
                    self.stdout.write('Dry run complete.')
                    # Raise exception to cancel transaction(s)
                    raise ProductImportException()

        except ProductImportException:
            pass


    def _split_and_convert_sizes(self, sizes_list):
        """
        Convert list to dict with height/width keys
        """
        sizes = []

        for size in sizes_list:
            size_item = size.split('x')
            sizes.append({"height": int(size_item[0]), "width": int(size_item[1])})

        return sizes

    def _get_remote_asset(self, url, filename):
        """
        Get a remote asset through an url, create a temporary file, and upload
        asset locally.
        """

        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        response = session.get(url, stream=True)

        if response.status_code != requests.codes.ok:
            raise RuntimeError(f'Remote asset returned statuscode {response.status_code}')

        lf = NamedTemporaryFile()

        for block in response.iter_content(1024 * 8):

            if not block:
                break

            lf.write(block)

        return File(lf, filename)
