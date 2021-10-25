from django.db import models


class ProductStatus(models.IntegerChoices):
    DRAFT = 1, 'Draft'
    HIDDEN = 2, 'Hidden'
    AVAILABLE = 3, 'Available'
    DISCONTINUED = 4, 'Discontinued'


class ProductStyles(models.TextChoices):
    CLASSIC = 'classic', 'Klassisk'
    CONCRETE = 'concrete', 'Betong'
    LUXURIOUS = 'luxurious', 'Luksus'
    MARBLE = 'marble', 'Marmor'
    NATURAL = 'natural', 'Naturlig'
    SCANDINAVIAN = 'scandinavian', 'Skandinavisk'
    STRUCTURED = 'structured', 'Strukturert'


class ProductApplications(models.TextChoices):
    CEILING = 'ceiling', 'Tak'
    FLOOR = 'floor', 'Gulv'
    TABLE = 'table', 'Bord'
    OUTDOORS = 'outdoors', 'Utendørs'
    SINK = 'sink', 'Vask'
    WALLS = 'walls', 'Vegger'


class ProductMaterials(models.TextChoices):
    CERAMIC = 'ceramic', 'Keramikk'
    METAL = 'metal', 'Metall'
    PORCELAIN = 'porcelain', 'Porselen'
    WOOD = 'wood', 'Tre'
