from django.db.models.signals import post_delete
from django.dispatch import receiver

from kitchens.models import Kitchen, KitchenDecor, KitchenPlywood


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