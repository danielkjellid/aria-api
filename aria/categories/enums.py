from django.db import models


class PromotionType(models.IntegerChoices):
    NEW = 1, "New"
