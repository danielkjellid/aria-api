from django.apps import AppConfig


class ProductCategorizationConfig(AppConfig):
    name = 'product_categorization'

    def ready(self) -> None:
        import product_categorization.signals
