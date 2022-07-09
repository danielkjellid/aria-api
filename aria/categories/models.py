from django.db import models
from django.utils.text import slugify

from mptt.models import MPTTModel, TreeForeignKey

from aria.categories.enums import PromotionType
from aria.categories.managers import CategoryManager, CategoryQueryset
from aria.core.models import BaseHeaderImageModel, BaseListImageModel, BaseModel
from aria.core.records import BaseHeaderImageRecord, BaseListImageRecord


class Category(MPTTModel, BaseModel, BaseHeaderImageModel, BaseListImageModel):
    """
    A category of which a product belongs to.
    """

    @property
    def category_image_directory_path(self) -> str:
        """Path of which to upload static assets"""
        if self.parent is not None:
            return (
                f"media/categories/{slugify(self.parent)}/"
                f"subcategories/{slugify(self.name)}"
            )
        return f"media/categories/{slugify(self.name)}"

    UPLOAD_PATH = category_image_directory_path  # type: ignore

    name = models.CharField(max_length=100, unique=False)
    slug = models.SlugField(
        max_length=50,
        help_text=(
            "A slug is a short label for something, containing only "
            "letters, numbers, underscores or hyphens. They’re generally "
            "used in URLs."
        ),
    )
    description = models.TextField(blank=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        verbose_name="parent",
        related_name="children",
        null=True,
        blank=True,
    )
    ordering = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        help_text="Order  in which the category should be displayed.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether the category should be treated as active.",
    )
    promotion_type = models.PositiveSmallIntegerField(
        choices=PromotionType.choices, null=True, blank=True, default=None
    )
    google_taxonomy_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=(
            "Used for classification in Google Merchant center. Link to ids: "
            "https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt"
        ),
    )

    objects = CategoryManager.from_queryset(CategoryQueryset)()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    class MPTTMeta:
        level_attr = "mptt_level"
        left_attr = "mptt_left"
        right_attr = "mptt_right"
        tree_id_attr = "mptt_tree_id"
        order_insertion_by = ["ordering"]

    def __str__(self) -> str:
        return (
            self.get_category_display()
            if self.is_active
            else f"{self.get_category_display()} (Inactive)"
        )

    def get_category_display(self) -> str:
        """
        Get formatted display name of category.
        """
        return (
            f"{self.parent.get_category_display()} > {self.name}"
            if self.parent
            else self.name
        )

    @property
    def is_primary(self) -> bool:
        """
        Property that returns True if the category is a top level
        category.
        """
        if self.mptt_level == 0:
            return True
        return False

    @property
    def is_secondary(self) -> bool:
        """
        Property that returns True if the category is a second level
        category.
        """
        if self.mptt_level == 1:
            return True
        return False

    @property
    def is_new(self) -> bool:
        """
        Property that checks if current promotion type is new.
        """
        if self.promotion_type == PromotionType.NEW:
            return True
        return False

    @property
    def images(self) -> BaseHeaderImageRecord:
        """
        Get category header images.
        """
        return BaseHeaderImageRecord(
            apply_filter=self.apply_filter,
            image_512x512=self.image_512x512.url,
            image_640x275=self.image_640x275.url,
            image_1024x575=self.image_1024x575.url,
            image_1024x1024=self.image_1024x1024.url,
            image_1536x860=self.image_1536x860.url,
            image_2048x1150=self.image_2048x1150.url,
        )

    def list_images(self) -> BaseListImageRecord:
        """
        Get category list images.
        """
        return BaseListImageRecord(
            image500x305=self.image500x305.url,
            image600x440=self.image600x440.url,
            image850x520=self.image850x520.url,
        )
