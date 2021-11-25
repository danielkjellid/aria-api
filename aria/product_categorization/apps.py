from django.apps import AppConfig


class ProductCategorizationConfig(AppConfig):
    name = "aria.product_categorization"

    def ready(self) -> None:
        import aria.product_categorization.signals
