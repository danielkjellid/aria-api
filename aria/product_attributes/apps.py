from django.apps import AppConfig


class ProductAttributesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aria.product_attributes"

    def ready(self) -> None:
        import aria.product_attributes.signals  # noqa: F401 pylint: disable=unused-import
