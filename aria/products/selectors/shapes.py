from aria.products.models import Shape
from aria.products.records import ProductShapeRecord


def shape_list() -> list[ProductShapeRecord]:
    """
    Returns a list of all shapes in the application.
    """

    shapes = Shape.objects.all().order_by("id")

    return [
        ProductShapeRecord(
            id=shape.id, name=shape.name, image=shape.image.url if shape.image else None
        )
        for shape in shapes
    ]
