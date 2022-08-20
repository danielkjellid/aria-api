from typing import TYPE_CHECKING

from django.db.models import F, Min, Prefetch

from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus

if TYPE_CHECKING:
    from aria.categories import models as category_models
    from aria.products import models


class SizeQuerySet(BaseQuerySet["models.Size"]):
    pass


class VariantQuerySet(BaseQuerySet["models.Variant"]):
    pass


class ColorQuerySet(BaseQuerySet["models.Color"]):
    pass


class ShapeQuerySet(BaseQuerySet["models.Shape"]):
    pass


class ProductQuerySet(BaseQuerySet["models.Product"]):
    def available(self) -> BaseQuerySet["models.Product"]:
        """
        Get available, sellable, product options.
        """

        return self.filter(status=ProductStatus.AVAILABLE)

    def with_active_categories(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetches active categories connected to a product.

        Used in together with the category_tree_active_list_for_product()
        selector that will use the prefetched attribute, active_categories, set
        by this manager method.
        """

        from aria.categories.models import Category

        active_categories = Category.objects.active()

        prefetched_children = Prefetch(
            "children", queryset=active_categories, to_attr="active_children"
        )
        active_categories = active_categories.prefetch_related(prefetched_children)

        prefetched_categories = Prefetch(
            "categories", queryset=active_categories, to_attr="active_categories"
        )

        return self.prefetch_related(prefetched_categories)

    def with_available_options(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetch related product options, variants and sizes.
        """

        from aria.products.models import ProductOption

        available_product_options = ProductOption.objects.available()

        available_product_options = available_product_options.select_related(
            "variant", "size"
        )

        prefetched_options = Prefetch(
            "options", queryset=available_product_options, to_attr="available_options"
        )

        return self.prefetch_related(prefetched_options)

    def with_available_options_unique_variants(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetch a set of unique product variants.
        """

        from aria.products.models import ProductOption

        available_product_options_variants = (
            ProductOption.objects.available()
            .select_related("variant")
            .distinct("variant_id")
        )

        prefetched_unique_variants = Prefetch(
            "options",
            queryset=available_product_options_variants,
            to_attr="available_options_unique_variants",
        )

        return self.prefetch_related(prefetched_unique_variants)

    def with_images(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetch a product's images.
        """

        return self.prefetch_related("images")

    def with_colors(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetch a product's colors.
        """

        return self.prefetch_related("colors")

    def with_shapes(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetch a product's shapes.
        """

        return self.prefetch_related("shapes")

    def with_files(self) -> BaseQuerySet["models.Product"]:
        """
        Prefetch a product's files.
        """

        return self.prefetch_related("files")

    def annotate_from_price(self) -> BaseQuerySet["models.Product"]:
        """
        Annotate a product's from price based on lowest options price
        available.
        """

        return self.annotate(annotated_from_price=Min("options__gross_price"))

    def preload_for_list(self) -> BaseQuerySet["models.Product"]:
        """
        Utility to avoid n+1 queries
        """

        qs = (
            self.select_related("supplier")
            .with_active_categories()
            .with_colors()
            .with_shapes()
            .with_available_options_unique_variants()
            .annotate_from_price()
        )

        return qs

    def by_category(
        self, category: "category_models.Category", ordered: bool = True
    ) -> BaseQuerySet["models.Product"]:
        """
        Get all products related to a specific category.
        """

        # Prepare queryset and get active descendants
        categories = category.get_descendants(include_self=True).active()

        products = self.filter(
            status=ProductStatus.AVAILABLE, categories__in=categories
        )

        if ordered:
            products.annotate(
                _ordering=categories.values_list("ordering")[:1]
            ).order_by(F("_ordering").asc(nulls_last=True), "name")

        return products


class ProductImageQuerySet(BaseQuerySet["models.ProductImage"]):
    pass


class ProductFileQuerySet(BaseQuerySet["models.ProductFile"]):
    pass


class ProductOptionQuerySet(BaseQuerySet["models.ProductOption"]):
    def available(self) -> BaseQuerySet["models.ProductOption"]:
        """
        Get available, sellable, product options.
        """

        return self.filter(status=ProductStatus.AVAILABLE)
