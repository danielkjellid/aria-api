from django.db import models


class ProductStatus(models.IntegerChoices):
    DRAFT = 1, 'Draft'
    HIDDEN = 2, 'Hidden'
    AVAILABLE = 3, 'Available'
    DISCONTINUED = 4, 'Discontinued'