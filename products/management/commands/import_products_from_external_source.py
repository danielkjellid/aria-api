from typing import Tuple
import requests
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils.text import slugify
from products.enums import ProductStatus
from suppliers.models import Supplier
from products.models import Product, ProductFile, ProductSiteState, Size, Variant, ProductOption
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
                for iteration, data in enumerate(products_data):

                    self.stdout.write(f'Currently processing {iteration + 1} of {len(products_data)} products')

                    # Sanity check to check that all necessary
                    # keys are present.
                    for required_key in required_keys:
                        assert required_key in data.keys()


                    variants = data.get('variants')
                    files = data.get('files')

                    # Create products and manipulate sizes
                    created_product, sizes_dict_list = self._create_imported_product(supplier=supplier, **data)

                    # Add product to m2m site rel.
                    self.stdout.write('Adding active site to product...')
                    created_product.sites.add(site)
                    created_product.save()
                    self.stdout.write('Active site added.')

                    # Create site state for m2m rel.
                    self.stdout.write('Creating site state...')
                    self._create_product_site_rel(site=site, product=created_product)

                    # Create files instances
                    self.stdout.write('Creating files...')
                    self._create_product_files(files=files, product=created_product, confirm=confirm)

                    # Get or create variants instances
                    self.stdout.write('Fetching/creating variants...')
                    variants_to_link = self._create_and_get_product_variants_to_link(variants=variants, confirm=confirm)

                    # Get or create sizes instances
                    self.stdout.write('Fetching/creating sizes...')
                    sizes_to_link = self._create_and_get_sizes_to_link(sizes=sizes_dict_list)

                    # Create product options to link sizes and variants
                    self.stdout.write('Linking sizes and variants to product...')
                    self._get_and_link_sizes_variants(variants=variants_to_link, sizes=sizes_to_link, product=created_product)

                    # End of operation
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

    def _create_imported_product(self, supplier: "Supplier", **kwargs) -> Tuple["Product", list]:
        """
        Create the product itself, and manipulate size list (need to check if special
        character is present in sizes list).
        """

        product_name = kwargs.get('collection_name')
        short_description = kwargs.get("short_description_nor", None)
        description = kwargs.get("description_nor")
        sizes = kwargs.get('sizes')

        # Not every datasource has a short_desc, therefore, we get the first
        # sentence of desc, and extracts it.
        if short_description is None and description is not None:
            short_description = f'{description.split(".")[0]}.'
            description = f'{description.partition(".")[2].strip()}.'

        # This variable is determined if there is an
        # asterix present in the sizes string
        is_special_size = False

        # Convert sizes from list to string, splitting on ","
        # and removing whitespace
        sizes_list = [size.strip() for size in sizes.split(',')]

        # Handle if product comes in special sizes
        if '*' in sizes_list:
            is_special_size = True
            sizes_list.remove('*')

        created_product = Product.objects.create(
            name=product_name,
            supplier=supplier,
            status=ProductStatus.DRAFT,
            slug=f'{slugify(supplier.name)}-{slugify(product_name)}',
            short_description=short_description,
            description=description,
            available_in_special_sizes=is_special_size,
            is_imported_from_external_source=True,
        )

        self.stdout.write(f'Product {created_product.name} created.')

        # Reiterate over the array and split variables by delimiter
        # return it as a list of dicts with keys height and width.
        sizes_dict_list = self._split_and_convert_sizes(sizes_list)

        return created_product, sizes_dict_list


    def _create_product_site_rel(self, site: "Site", product: "Product") -> None:
        """
        Create product site state for m2m rel.
        """

        ProductSiteState.objects.create(
            site=site,
            product=product,
            gross_price=0.0,
            display_price=False,
            can_be_purchased_online=False,
            can_be_picked_up=False,
            supplier_purchase_price=0.0,
            supplier_shipping_cost=0.0
        )
        self.stdout.write('Site state created.')


    def _create_product_files(self, files: "list[str]", product: "Product", confirm: "bool") -> None:
        """
        Create file instance belloning to product.
        """

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

            ProductFile.objects.create(
                product=product,
                name=name,
                file=self._get_remote_asset(value, name) if confirm else None
            )
            self.stdout.write(f'File {name} added.')
        self.stdout.write('All files created.')


    def _create_and_get_product_variants_to_link(self, variants: "list", confirm: "bool") -> "list":
        """
        Create or get appropriate variants and append them to a list to link
        it and sizes later.
        """

        variants_to_link = []

        for variant in variants:
            created_variant = Variant.objects.get_or_create(
                name=variant['name'].title(),
                status=ProductStatus.AVAILABLE,
                thumbnail=self._get_remote_asset(variant['image_url'], variant['name']) if confirm else None,
            )

            variants_to_link.append(created_variant)
            self.stdout.write(f'Variant {variant["name"].title()} added.')
        self.stdout.write('All variants created and ready to link.')

        return variants_to_link


    def _create_and_get_sizes_to_link(self, sizes: "list") -> "list":
        """
        Create or get appropriate sizes and append them to a list to link
        it and variants later.
        """

        sizes_to_link = []

        for size_set in sizes:
            height = size_set.get('height')
            width = size_set.get('width')

            size = Size.objects.get_or_create(
                width=width,
                height=height
            )

            sizes_to_link.append(size)
        self.stdout.write('All sizes fetched/created and ready to link.')

        return sizes_to_link

    def _get_and_link_sizes_variants(self, variants: "list", sizes: "list", product: "Product") -> None:
        """
        Create product options by combining variants with sizes.
        """

        for variant, created in variants:
            if len(sizes) > 0:
                for size, created in sizes:
                    ProductOption.objects.create(
                        product=product,
                        variant=variant,
                        size=size,
                        gross_price=0.00
                    )
            else:
                ProductOption.objects.create(
                    product=product,
                    variant=variant,
                    size=None,
                    gross_price=0.00
                )

        self.stdout.write('Sizes and variants linked and added to product.')
