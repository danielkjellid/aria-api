from django.db import models


class ProductStatus(models.IntegerChoices):
    DRAFT = 1, "Draft"
    HIDDEN = 2, "Hidden"
    AVAILABLE = 3, "Available"
    DISCONTINUED = 4, "Discontinued"


class ProductStyles(models.TextChoices):
    CLASSIC = "classic", "Klassisk"
    CONCRETE = "concrete", "Betong"
    LUXURIOUS = "luxurious", "Luksus"
    MARBLE = "marble", "Marmor"
    NATURAL = "natural", "Naturlig"
    SCANDINAVIAN = "scandinavian", "Skandinavisk"
    STRUCTURED = "structured", "Strukturert"
    WOODENSTRUCTURE = "woodenstructure", "Trestruktur"
    MODERN = "modern", "Moderne"
    CIRCULAR = "circular", "Rundt"
    SQUARE = "square", "Firkantet"
    OVAL = "oval", "Ovalt"
    MIRROR_WITH_LIGHT = "mirrorwithlight", "Speil med lys"
    INDUSTRIAL = "industrial", "Industriell"


class ProductApplications(models.TextChoices):
    CEILING = "ceiling", "Tak"
    FLOOR = "floor", "Gulv"
    TABLE = "table", "Bord"
    OUTDOORS = "outdoors", "Utendørs"
    SINK = "sink", "Vask"
    WALLS = "walls", "Vegger"


class ProductMaterials(models.TextChoices):
    CERAMIC = "ceramic", "Keramikk"
    METAL = "metal", "Metall"
    PORCELAIN = "porcelain", "Porselen"
    WOOD = "wood", "Tre"
    OAK = "oak", "Eik"
    MDF = "mdf", "MDF"
    LAMINATE = "laminate", "Laminat"
    TEAK = "teak", "Teak"
    MIRROR = "mirror", "Speil"
    BRUSHED_STEEL = "brushedsteel", "Pusset stål"
    STAINLESS_STEEL = "stainlesssteel", "Rustfritt stål"
    COMPOSITE = "composite", "Kompositt"


class ProductUnit(models.IntegerChoices):
    SQUARE_METER = 1, "m2"
    PCS = 2, "stk"


class NewProductMaterials(models.TextChoices):
    COMPOSITE = "kompositt", "Kompositt"
    STAINLESS_STEEL = "rustfritt stål", "Rustfritt stål"
    BRUSHED_STEEL = "pusset stål", "Pusset stål"
    WOOD = "tre", "Tre"
    LAMINATE = "laminat", "Laminat"
    GLASS = "glass", "Glass"
    MARBLE = "marmor", "Marmor"


class ProductRooms(models.TextChoices):
    BATHROOM = "badrom", "Bad"
    KITCHEN = "kjøkken", "Kjøkken"
    LIVING_ROOMS = "stue gang oppholdsrom", "Stue, gang og oppholdsrom"
    OUTDOOR = "uterom", "Uterom"
