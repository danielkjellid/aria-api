from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = "aria.products"

    def ready(self) -> None:
        import aria.products.signals  # noqa: F401
