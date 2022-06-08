from django.db.models import F, Prefetch

from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus


class SizeQuerySet(BaseQuerySet):
    pass


class VariantQuerySet(BaseQuerySet):
    pass


class ColorQuerySet(BaseQuerySet):
    pass


class ShapeQuerySet(BaseQuerySet):
    pass


class ProductQuerySet(BaseQuerySet):
    def with_active_categories(self):
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

    def with_available_options(self):

        from aria.products.models import ProductOption

        available_product_options = ProductOption.objects.available()

        available_product_options = available_product_options.select_related(
            "variant", "size"
        )

        prefetched_options = Prefetch(
            "options", queryset=available_product_options, to_attr="available_options"
        )

        return self.prefetch_related(prefetched_options)

    def annotate_site_state_data(self):

        from aria.products.models import ProductSiteState

        option = ProductSiteState.on_site.filter(product__in=self).values(
            "display_price",
            "gross_price",
            "can_be_picked_up",
            "can_be_purchased_online",
        )

        return self.annotate(
            display_price=option.values("display_price")[:1],
            from_price=option.values("gross_price")[:1],
            can_be_picked_up=option.values("can_be_picked_up")[:1],
            can_be_purchased_online=option.values("can_be_purchased_online")[:1],
        )

    def preload_for_list(self):
        """
        Utility to avoid n+1 queries
        """

        qs = self.select_related("supplier").prefetch_related(
            "categories",
            "colors",
            "shapes",
            "images",
            "shapes",
            "options",
            "files",
        )

        return qs

    def by_category(self, category, ordered: bool = True):
        # Prepare queryset and get active decendants
        categories = category.get_descendants(include_self=True).active()

        products = self.filter(
            status=ProductStatus.AVAILABLE, categories__in=categories
        )

        if ordered:
            products.annotate(
                _ordering=categories.values_list("ordering")[:1]
            ).order_by(F("_ordering").asc(nulls_last=True), "name")

        return products


class ProductImageQuerySet(BaseQuerySet):
    pass


class ProductFileQuerySet(BaseQuerySet):
    pass


class ProductSiteStateQuerySet(BaseQuerySet):
    pass


class ProductOptionQuerySet(BaseQuerySet):
    def available(self):
        """
        Get available, sellable, product options.
        """

        return self.filter(status=ProductStatus.AVAILABLE)
