from decimal import Decimal
from tempfile import NamedTemporaryFile
from typing import Tuple

from django.contrib.sites.models import Site
from django.core.files import File
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils.text import slugify

import requests

from aria.product_categorization.models import SubCategory
from aria.products.enums import ProductStatus
from aria.products.models import (
    Product,
    ProductFile,
    ProductOption,
    Size,
    Variant,
)
from aria.suppliers.models import Supplier


class ProductImportException(Exception):
    """
    Exception raised to rollback transaction
    """


class Command(BaseCommand):
    help = "Imports products form a given JSON source"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--supplier_id",
            type=int,
            default=None,
            help="Which supplier does the products bellong to?",
            required=True,
        )
        parser.add_argument(
            "--source",
            type=str,
            default=None,
            help="Source of which to get the products from",
            required=True,
        )
        parser.add_argument(
            "--add_absorption",
            action="store_true",
            dest="add_absorption",
            help="Tiles need the absorption attr, this sets it to the default 0,05%",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            dest="confirm",
            help="Indicates that the operation should be executed",
        )

    def handle(self, *args, **options) -> None:
        # Get given parameteres
        supplier_id = options["supplier_id"]
        source = options["source"]
        add_absorption = options["add_absorption"]
        confirm = options["confirm"]

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
                    self.stdout.write("#######################")
                    self.stdout.write("###     DRY RUN     ###")
                    self.stdout.write("#######################")

                # Start loop and creation of products
                for iteration, data in enumerate(products_data):

                    assert data[
                        "collection_name"
                    ], "Key collection_name is missing, but is required"
                    assert data[
                        "description_nor"
                    ], "Key description_nor is missing, but is required"
                    assert data["sizes"], "Key sizes is missing, but is required"

                    self.stdout.write(
                        f"Currently processing {iteration + 1} of {len(products_data)} products"
                    )

                    variants = data.get("variants", None)
                    files = data.get("files", None)
                    categories = data.get("categories", None)

                    # Create products and manipulate sizes
                    created_product, sizes_dict_list = self._create_imported_product(
                        supplier=supplier, add_absorption=add_absorption, **data
                    )

                    # Add product to m2m site rel.
                    self.stdout.write("Adding active site to product...")
                    created_product.sites.add(site)
                    created_product.save()
                    self.stdout.write("Active site added.")

                    if categories is not None:
                        self.stdout.write("Adding categories to product...")
                        self._create_product_category_rels(
                            categories=categories, product=created_product
                        )
                        self.stdout.write("All categories added.")

                    # Create site state for m2m rel.
                    self.stdout.write("Creating site state...")
                    self._create_product_site_rel(site=site, product=created_product)

                    # Create files instances
                    if files is not None:
                        self.stdout.write("Creating files...")
                        self._create_product_files(
                            files=files, product=created_product, confirm=confirm
                        )

                    # Get or create variants instances
                    if variants is not None:
                        self.stdout.write("Fetching/creating variants...")
                        variants_to_link = (
                            self._create_and_get_product_variants_to_link(
                                variants=variants, confirm=confirm
                            )
                        )

                    # Get or create sizes instances
                    self.stdout.write("Fetching/creating sizes...")
                    sizes_to_link = self._create_and_get_sizes_to_link(
                        sizes=sizes_dict_list
                    )

                    # Create product options to link sizes and variants
                    price = data.get("price", None)
                    self.stdout.write("Linking sizes and variants to product...")
                    self._get_and_link_sizes_variants(
                        variants=variants_to_link if variants else [],
                        sizes=sizes_to_link,
                        product=created_product,
                        price=price,
                    )

                    # End of operation
                    self.stdout.write("----------------------------------------------")

                if not confirm:
                    self.stdout.write("Dry run complete.")
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
            size_items = size.split("x")
            if len(size_items) == 1:
                sizes.append(
                    {
                        "height": None,
                        "width": None,
                        "depth": None,
                        "circumference": size_items[0],
                    }
                )
            elif len(size_items) == 3:
                sizes.append(
                    {
                        "height": Decimal(size_items[0]),
                        "width": Decimal(size_items[1]),
                        "depth": Decimal(size_items[2]),
                        "circumference": None,
                    }
                )
            else:
                sizes.append(
                    {
                        "height": Decimal(size_items[0]),
                        "width": Decimal(size_items[1]),
                        "depth": None,
                        "circumference": None,
                    }
                )

        return sizes

    def _get_remote_asset(self, url, filename):
        """
        Get a remote asset through an url, create a temporary file, and upload
        asset locally.
        """

        session = requests.Session()
        session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
        response = session.get(url, stream=True)

        if response.status_code != requests.codes.ok:
            raise RuntimeError(
                f"Remote asset returned statuscode {response.status_code}"
            )

        lf = NamedTemporaryFile()

        for block in response.iter_content(1024 * 8):

            if not block:
                break

            lf.write(block)

        return File(lf, f"{filename}.pdf")

    def _create_imported_product(
        self, supplier: "Supplier", add_absorption: "bool", **kwargs
    ) -> Tuple["Product", list]:
        """
        Create the product itself, and manipulate size list (need to check if special
        character is present in sizes list).
        """

        product_name = kwargs.get("collection_name")
        short_description = kwargs.get("short_description_nor", None)
        description = kwargs.get("description_nor")
        sizes = kwargs.get("sizes")

        # Not every datasource has a short_desc, therefore, we get the first
        # sentence of desc, and extracts it.
        if short_description is None and description is not None:
            short_description = f'{description.split(".")[0]}.'
            description = f'{description.partition(".")[2].strip()}'

        # This variable is determined if there is an
        # asterix present in the sizes string
        is_special_size = False

        # Convert sizes from list to string, splitting on ","
        # and removing whitespace
        sizes_list = [size.strip() for size in sizes.split(",")]

        # Handle if product comes in special sizes
        if "*" in sizes_list:
            is_special_size = True
            sizes_list.remove("*")

        created_product = Product.objects.create(
            name=product_name.title(),
            supplier=supplier,
            status=ProductStatus.DRAFT,
            slug=f"{slugify(supplier.name)}-{slugify(product_name)}",
            short_description=short_description,
            description=description,
            available_in_special_sizes=is_special_size,
            is_imported_from_external_source=True,
            absorption=0.05 if add_absorption is True else None,
        )

        self.stdout.write(f"Product {created_product.name} created.")

        # Reiterate over the array and split variables by delimiter
        # return it as a list of dicts with keys height and width.
        sizes_dict_list = self._split_and_convert_sizes(sizes_list)

        return created_product, sizes_dict_list

    def _create_product_category_rels(
        self, categories: "list[str]", product: "Product"
    ) -> None:
        splitted_category_slugs = [
            category.strip() for category in categories.split(",")
        ]

        for slug in splitted_category_slugs:
            cat = SubCategory.objects.get(slug=slug)
            product.category.add(cat)

    def _create_product_files(
        self, files: "list", product: "Product", confirm: "bool"
    ) -> None:
        """
        Create file instance belloning to product.
        """

        for file in files:

            assert file[
                "name"
            ], "Key name in files list does not exist, but is required"
            assert file[
                "file_url"
            ], "Key file_url in files list does not exist, but is required"

            ProductFile.objects.create(
                product=product,
                name=file["name"],
                file=self._get_remote_asset(file["file_url"], file["name"])
                if confirm
                else None,
            )
            self.stdout.write(f"File {file['name']} added.")
        self.stdout.write("All files created.")

    def _create_and_get_product_variants_to_link(
        self, variants: "list", confirm: "bool"
    ) -> "list":
        """
        Create appropriate variants and append them to a list to link
        it and sizes later.
        """

        variants_to_link = []

        for variant in variants:
            name = variant.get("name", None)
            image_url = variant.get("image_url", None)

            if name is None and image_url is None:
                continue

            # If image url is not specified, we assume to use an already
            # existing variant.
            if name is not None and image_url is None:
                gotten_variant = None
                try:
                    gotten_variant = Variant.objects.get(name=name.title())
                    self.stdout.write(f"Existing variant {gotten_variant.name} added.")
                except Variant.MultipleObjectsReturned:
                    gotten_variant = Variant.objects.get(
                        name=name.title(), is_standard=True
                    )
                    self.stdout.write(
                        f"Existing standard variant {gotten_variant.name} added."
                    )

                variants_to_link.append(gotten_variant)
            else:
                # If image_url exists, we create a new variant with correct
                # properties.
                created_variant = Variant.objects.create(
                    name=name.title(),
                )

                # Since the file needs the id to be created, save the thumbnail after
                # creation.
                if confirm:
                    file = self._get_remote_asset(image_url, name)
                    created_variant.thumbnail.save(f"{slugify(name)}", file)

                variants_to_link.append(created_variant)
                self.stdout.write(f"Variant {name.title()} added.")
        self.stdout.write("All variants gotten/created and ready to link.")

        return variants_to_link

    def _create_and_get_sizes_to_link(self, sizes: "list") -> "list":
        """
        Create or get appropriate sizes and append them to a list to link
        it and variants later.
        """

        sizes_to_link = []

        for size_set in sizes:
            size = Size.objects.get_or_create(**size_set)
            sizes_to_link.append(size)
        self.stdout.write("All sizes fetched/created and ready to link.")

        return sizes_to_link

    def _get_and_link_sizes_variants(
        self, variants: "list", sizes: "list", product: "Product", price: "Decimal"
    ) -> None:
        """
        Create product options by combining variants with sizes.
        """

        if len(sizes) > 0 and len(variants) > 0:
            for variant in variants:
                for size, _ in sizes:
                    ProductOption.objects.create(
                        product=product,
                        variant=variant,
                        size=size,
                        gross_price=price if price else 0.00,
                        status=ProductStatus.AVAILABLE,
                    )

        if len(sizes) > 0 and len(variants) <= 0:
            for size, _ in sizes:
                ProductOption.objects.create(
                    product=product,
                    variant=None,
                    size=size,
                    gross_price=price if price else 0.00,
                    status=ProductStatus.AVAILABLE,
                )

        if len(variants) > 0 and len(sizes) <= 0:
            for variant in variants:
                ProductOption.objects.create(
                    product=product,
                    variant=variant,
                    size=None,
                    gross_price=price if price else 0.00,
                    status=ProductStatus.AVAILABLE,
                )

        self.stdout.write("Sizes and variants linked and added to product.")
