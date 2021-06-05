from django.db import models
from core.utils.shapes import Rectangle
from core.utils.measures import Measure
from measurement.measures import Distance


class MachineManager(models.Manager):
    def create_machine(self, **kwargs):
        mapping = {
            Machine.PRESS : PressMachine,
            Machine.OTHERS : Machine
        }
        type = kwargs.get('type', Machine.OTHERS)
        clazz = mapping[type]
        machine = clazz.objects.create(**kwargs)
        return machine


class Machine(models.Model):
    PRESS = 'press'
    OTHERS = 'others'
    TYPES = [
        (PRESS, 'Press'),
        (OTHERS, 'Others'),
    ]
    objects = MachineManager()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPES, null=False, blank=False)


class PressMachine(Machine):
    min_sheet_length = models.FloatField(blank=True, default=0)
    max_sheet_length = models.FloatField(blank=True, default=0)
    min_sheet_width = models.FloatField(blank=True, default=0)
    max_sheet_width = models.FloatField(blank=True, default=0)
    uom = models.CharField(max_length=30, default='mm',
        choices=Measure.UNITS[Measure.DISTANCE])

    def add_parent_sheet(self, width, length, size_uom, 
        padding_top=None, padding_right=None,
        padding_bottom=None, padding_left=None):

        parent = ParentSheet.objects.create(machine=self,
            width_value=width, length_value=length, size_uom=size_uom,
            padding_top=padding_top, padding_right=padding_right,
            padding_bottom=padding_bottom, padding_left=padding_left)

        return parent


class ParentSheet(Rectangle):
    machine = models.ForeignKey(PressMachine, on_delete=models.CASCADE, 
        related_name='parent_sheets')
    padding_top = models.FloatField(null=True, blank=True, default=0)
    padding_right = models.FloatField(null=True, blank=True, default=0)
    padding_bottom = models.FloatField(null=True, blank=True, default=0)
    padding_left = models.FloatField(null=True, blank=True, default=0)

    @property
    def pack_width(self):
        return self.width_value - self.padding_x

    @property
    def pack_length(self):
        return self.length_value - self.padding_y

    @property
    def padding(self):
        return (self.padding_top, self.padding_right, 
            self.padding_bottom, self.padding_left)
    
    @property
    def padding_x(self):
        return self.padding_right + self.padding_left
    
    @property
    def padding_y(self):
        return self.padding_top + self.padding_bottom

    def add_child_sheet(self, width, length, size_uom, 
        margin_top=None, margin_right=None,
        margin_bottom=None, margin_left=None):

        child = ChildSheet.objects.create(parent=self,
            width_value=width, length_value=length, size_uom=size_uom,
            margin_top=margin_top, margin_right=margin_right,
            margin_bottom=margin_bottom, margin_left=margin_left)
            
        return child


class ChildSheet(Rectangle):
    parent = models.ForeignKey(ParentSheet, on_delete=models.CASCADE,
        related_name='child_sheets')
    margin_top = models.FloatField(blank=True, default=0)
    margin_right = models.FloatField(blank=True, default=0)
    margin_bottom = models.FloatField(blank=True, default=0)
    margin_left = models.FloatField(blank=True, default=0)

    @property
    def pack_width(self):
        return self.width_value + self.margin_x
    
    @property
    def pack_length(self):
        return self.length_value + self.margin_y

    @property
    def margin(self):
        return (self.margin_top, self.margin_right, 
            self.margin_bottom, self.margin_left)

    @property
    def margin_x(self):
        return self.margin_left + self.margin_right
    
    @property
    def margin_y(self):
        return self.margin_top + self.margin_bottom

    @property
    def packer(self):
        return self.parent.pack(self)

    @property
    def count(self):
        return len(self.packer)

    @property
    def usage(self):
        used_area = self.pack_width * self.pack_length * self.count
        total_area = self.parent.pack_width * self.parent.pack_length
        return (used_area / total_area)

    @property
    def wastage(self):
        return 1 - self.usage
