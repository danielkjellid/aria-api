
def cleanup_files_from_deleted_instance(sender, instance, *args, **kwargs):
    """
    Function to fire when a model instance is deleted, and we need to cleanup
    dangling associated files - deleting them from the system.
    """

    if instance and instance.thumbnail:
        instance.thumbnail.delete()

    if instance and instance.image:
        instance.image.delete()

    if instance and instance.file:
        instance.file.delete()