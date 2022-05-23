from aria.core.models import BaseHeaderImageModel
from aria.core.schemas.records import BaseHeaderImageRecord, BaseListImageRecord


def base_header_image_record(
    *, instance: BaseHeaderImageModel
) -> BaseHeaderImageRecord:
    """
    Utiltiy for quickly populating the BaseHeaderImageRecord.
    """

    return BaseHeaderImageRecord(
        apply_filter=instance.apply_filter,
        image_512x512=instance.image_512x512.url,
        image_640x275=instance.image_640x275.url,
        image_1024x575=instance.image_1024x575.url,
        image_1024x1024=instance.image_1024x1024.url,
        image_1536x860=instance.image_1536x860.url,
        image_2048x1150=instance.image_2048x1150.url,
    )


def base_list_image_record(*, instance: BaseListImageRecord) -> BaseListImageRecord:
    """
    Utiltiy for quickly populating the BaseListImageRecord.
    """

    return BaseListImageRecord(
        image500x305=instance.image500x305.url,
        image600x440=instance.image600x440.url,
        image850x520=instance.image850x520.url,
    )
