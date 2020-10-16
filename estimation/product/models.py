from django.db import models
from django.db.models import Q
from django_measurement.models import MeasurementField
from measurement.measures import Distance
from inventory.models import Item


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
    SHEET = 'sheet'
    PADDED = 'padded'
    CONTINUOUS = 'continuous'
    TYPES = [
        (SHEET, 'Sheet'),
        (PADDED, 'Padded'),
        (CONTINUOUS, 'Continuous')
    ]
    type = models.CharField(max_length=15, choices=TYPES)
    with_numbering = models.BooleanField(default=False)
    with_bir = models.BooleanField(default=False)
    with_amienda = models.BooleanField(default=False)

    @property
    def substrate_options(self):
        def __get_materials(paper_type):
            return Item.objects.filter(Q(type=paper_type) #& #Q(is_raw_material=True) &
                                       #Q(properties__length__gte=self.length)
                                       #((Q(properties__length__gte=self.length) &
                                       #  Q(properties__width__gt=self.width)) |
                                       # (Q(properties__length__gt=self.width) &
                                       #  Q(properties__width__gt=self.length)))
                                       )
        substrate = None
        if self.type == Form.PADDED or self.type == Form.SHEET:
            substrate = __get_materials(Item.PAPER_SHEET)
        else:
            substrate = __get_materials(Item.PAPER_ROLL)
        return substrate

    @property
    def ply_count(self):
        return len(FormPly.objects.filter(form__pk=self.pk))

    def add_ply(self, item, order):
        return FormPly.objects.create(form=self, item=item, order=order)


class FormPly(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    item = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True)
