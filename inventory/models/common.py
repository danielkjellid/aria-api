from django.db import models
from django.utils.translation import gettext_lazy as _


class Unit(models.IntegerChoices):
    SQUARE_METER = 1, _('m2')
    PCS = 2, _('stk')


class Status(models.IntegerChoices):
    DRAFT = 1, _('Draft')
    HIDDEN = 2, _('Hidden')
    AVAILABLE = 3, _('Available')
    DISCONTINUED = 4, _('Discontinued')