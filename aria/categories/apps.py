from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aria.categories"

    def ready(self) -> None:
        import aria.categories.signals  # noqa: F401 # pylint: disable=unused-import
