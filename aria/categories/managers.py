from django.db.models import Exists, IntegerField, OuterRef, Prefetch, Value

from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet


class CategoryManager(TreeManager):
    pass


class CategoryQueryset(TreeQuerySet):
    def active(self):
        """
        Returns active categories.
        """

        return self.exclude(
            # Get all current ant all parent categories
            Exists(
                self.model.objects.filter(
                    mptt_tree_id=OuterRef("mptt_tree_id"),
                    mptt_left__lte=OuterRef("mptt_left"),
                    mptt_right__gte=OuterRef("mptt_right"),
                    mptt_level__lte=OuterRef("mptt_level"),
                )
                .exclude(is_active=True)
                .values_list(Value(1, output_field=IntegerField()))
            )
        )

    def primary(self):
        """
        Returns all primary categories - note that we do not filter
        on active here, so only use backend.
        """

        return self.filter(mptt_level=0).order_by("ordering")

    def secondary(self):
        """
        Returns all secondary categories - meaning any category that
        is a child - note that we do not filter on active here, so
        only use backend.
        """

        return self.filter(mptt_level=1).order_by("ordering")

    def primary_and_secondary(self):
        """
        Returns all categories with their children.
        """

        return self.filter(mptt_level__in=[0, 1]).order_by(
            "ordering", "children__ordering"
        )

    def with_active_children(self):
        """
        Prefetch one level of active children
        """

        active_categories = self.model.objects.active().order_by("ordering")

        prefetch_children = Prefetch(
            "children", queryset=active_categories, to_attr="active_children"
        )

        self.prefetch_related(prefetch_children)
