from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aria.categories"

    def ready(self) -> None:
        import aria.product_categorization.signals  # noqa: F401
