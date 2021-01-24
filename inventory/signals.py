from django.db.models.signals import post_delete
from django.dispatch import receiver

from inventory.models.product import Product, ProductImage, ProductVariant, ProductFile
from inventory.models.kitchen import Kitchen, KitchenDecor, KitchenPlywood
from inventory.models.category import Category

"""
The signals bellow fires when a product (or individual image, variant thumbnail and file)
is deleted, and cleans up the associated files, deleting them from the system.
"""
@receiver(post_delete, sender=Product)
def delete_product_thumbnail(sender, instance, *args, **kwargs):
    if instance.thumbnail:
        instance.thumbnail.delete()

@receiver(post_delete, sender=ProductImage)
def delete_product_images(sender, instance, *args, **kwargs):
    if instance.image:
        instance.image.delete()

@receiver(post_delete, sender=ProductVariant)
def delete_product_variant_thumbnail(sender, instance, *args, **kwargs):
    if instance.thumbnail:
        instance.thumbnail.delete()

@receiver(post_delete, sender=ProductFile)
def delete_product_file(sender, instance, *args, **kwargs):
    if instance.file:
        instance.file.delete()


"""
The signals bellow fires when a kitchen (or individual decor or plywood) is deleted,
and cleans up the associated files, deleting them from the system.
"""
@receiver(post_delete, sender=Kitchen)
def delete_kitchen_image(sender, instance, *args, **kwargs):
    if instance.image:
        instance.image.delete()

@receiver(post_delete, sender=KitchenPlywood)
def delete_kitchen_plywood_image(sender, instance, *args, **kwargs):
    if instance.image:
        instance.image.delete()

@receiver(post_delete, sender=KitchenDecor)
def delete_kitchen_decor_image(sender, instance, *args, **kwargs):
    if instance.image:
        instance.image.delete()


"""
The signal bellow fires when a category is deleted, and cleans up the associated
files, deleting them from the system.
"""
@receiver(post_delete, sender=Category)
def delete_category_image(sender, instance, *args, **kwargs):
    if instance.image:
        instance.image.delete()
