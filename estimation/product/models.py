from django.db import models
from django.db.models import Q
from django_measurement.models import MeasurementField
from measurement.measures import Distance
from ...inventory.models import Item


class Product(models.Model):
    name = models.CharField(max_length=40)
    length = MeasurementField(measurement=Distance)
    width = MeasurementField(measurement=Distance)

    @property
    def finished_size(self):
        return {'length': self.length, 'width': self.width}

    @property
    def flat_size(self):
        return {'length': self.length, 'width': self.width}


class Form(Product):
    PADDED = 'padded'
    CONTINUOUS = 'continuous'
    TYPES = [
        (PADDED, 'Padded'),
        (CONTINUOUS, 'Continuous')
    ]
    type = models.CharField(max_length=15, choices=TYPES)
    ply_count = models.IntegerField(default=1)

    @property
    def substrates(self):
        def __get_materials(paper_type):
            return Item.objects.filter(Q(type=paper_type) & Q(is_raw_material=True) &
                                       ((Q(properties__length__gte=self.length) &
                                         Q(properties__width__gt=self.width)) |
                                        (Q(properties__length__gt=self.width) &
                                         Q(properties__width__gt=self.length))))
        substrate = None
        if self.type == Form.PADDED:
            substrate = __get_materials(Item.PAPER_SHEET)
        else:
            substrate = __get_materials(Item.PAPER_ROLL)
        return substrate
