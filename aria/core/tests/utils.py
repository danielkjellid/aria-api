from io import BytesIO

from django.core.files.images import ImageFile

from PIL import Image


def create_image_file(
    *, name: str, extension: str = "JPEG", width: int | float, height: int | float
) -> ImageFile:
    """
    Create a ImageFile representation usable in tests.
    """

    file = BytesIO()
    image = Image.new("L", size=(width, height))
    image.save(file, extension.lower())
    file.name = f"{name}.{extension.lower()}"
    file.seek(0)

    return ImageFile(file)
