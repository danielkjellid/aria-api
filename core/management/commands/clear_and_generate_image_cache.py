from typing import Tuple
from imagekit.utils import get_cache
import requests
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils.text import slugify
from kitchens.models import Kitchen
from products.enums import ProductStatus
from suppliers.models import Supplier
from products.models import Product, ProductFile, ProductImage, ProductSiteState, Size, Variant, ProductOption
from product_categorization.models import Category
from tempfile import NamedTemporaryFile


class ProductImportException(Exception):
    """
    Exception raised to rollback transaction
    """

class Command(BaseCommand):
    help = 'Clear image chache and generate new one'

    def handle(self, *args, **options) -> None:

        get_cache().clear()

        product_images = ProductImage.objects.all()
        categories = Category.objects.all()
        kitchens = Kitchen.objects.all()
        variants = Variant.objects.all()

        for product_image in product_images:
            name = product_image.image.name

            if name:
                product_image.image_512x512.generate(save=True)
                product_image.image_1024x1024.generate(save=True)
                product_image.image_640x275.generate(save=True)
                product_image.image_1024x575.generate(save=True)
                product_image.image_1536x860.generate(save=True)
                product_image.image_2048x1150.generate(save=True)

