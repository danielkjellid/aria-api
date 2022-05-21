from ninja import Schema, Field


class ProductDetailOutput(Schema):
    id: int
    status: str
    unit: str
    name: str
    description: str = Field(
        ..., alias="new_description"
    )  # TODO: remove source when migrated to new_desc

    def resolve_status(self):
        pass

    def response_unit(self):
        pass
