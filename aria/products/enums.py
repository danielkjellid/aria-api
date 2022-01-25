from django.db import models


class ProductStatus(models.IntegerChoices):
    DRAFT = 1, "Draft"
    HIDDEN = 2, "Hidden"
    AVAILABLE = 3, "Available"
    DISCONTINUED = 4, "Discontinued"


class ProductUnit(models.IntegerChoices):
    SQUARE_METER = 1, "m2"
    PCS = 2, "stk"


class ProductMaterials(models.TextChoices):
    COMPOSITE = "kompositt", "Kompositt"
    STAINLESS_STEEL = "rustfritt stål", "Rustfritt stål"
    BRUSHED_STEEL = "pusset stål", "Pusset stål"
    METAL = "metall", "Metall"
    WOOD = "tre", "Tre"
    LAMINATE = "laminat", "Laminat"
    GLASS = "glass", "Glass"
    MARBLE = "marmor", "Marmor"


class ProductRooms(models.TextChoices):
    BATHROOM = "badrom", "Bad"
    KITCHEN = "kjøkken", "Kjøkken"
    LIVING_ROOMS = "stue gang oppholdsrom", "Stue, gang og oppholdsrom"
    OUTDOOR = "uterom", "Uterom"
