import math
from django.db import models
from core.utils.shapes import Rectangle
from core.utils.measures import Measure, Quantity
from measurement.measures import Distance
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from estimation.product.models import Material
from inventory.models import Item
import inflect

_inflect = inflect.engine()

class Estimate:
    def __init__(self, run_count, item_count):
        self.run_count = run_count
        self.item_count = item_count
        self.length = 0
        self.area = 0
        self.volume = 0
        self.perimeter = 0


class MachineManager(PolymorphicManager):
    def create_machine(self, **kwargs):
        mapping = {
            Machine.SHEET_FED_PRESS : SheetFedPressMachine
        }
        type = kwargs.get('type', Machine.SHEET_FED_PRESS)
        clazz = mapping[type]
        machine = clazz.objects.create(**kwargs)
        return machine


class Machine(PolymorphicModel):
    SHEET_FED_PRESS = 'SheetFedPressMachine'
    TYPES = [
        (SHEET_FED_PRESS, 'Sheet-fed Press'),
    ]

    objects = MachineManager()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=30, choices=TYPES, null=False, blank=False)

    def estimate(self, **kwargs):
        pass

    def __str__(self):
        return self.name


class PressMachine(Machine):
    OFFSET = 'Offset'
    DIGITAL = 'Digital'
    LETTERPRESS = 'Letterpress'
    PROCESS_TYPES = [
        (OFFSET, 'Offset'),
        (DIGITAL, 'Digital'),
        (LETTERPRESS, 'Letterpress')
    ]
    process_type = models.CharField(max_length=15, choices=PROCESS_TYPES, 
        null=False, blank=False)


class SheetFedPressMachine(PressMachine):
    min_sheet_length = models.FloatField(default=0)
    max_sheet_length = models.FloatField(default=0)
    min_sheet_width = models.FloatField(default=0)
    max_sheet_width = models.FloatField(default=0)
    uom = models.CharField(max_length=30, default='mm',
        choices=Measure.UNITS[Measure.DISTANCE])

    def estimate(self, input:Item, output:Material, quantity, bleed=False):
        if input.type == output.type == Item.PAPER:
            child_sheets = (
                ChildSheet.objects
                    .filter(parent__machine=self)
                    .order_by('width_value', 'length_value')
            )
            match = None

            for child_sheet in child_sheets:
                if child_sheet.has_bleed == bleed and child_sheet.gte(output) \
                        and input.properties.gte(child_sheet.parent):
                    match = child_sheet
                    break

            if match is not None:
                parent_sheet_per_item = input.properties.pack(match.parent)
                child_sheet_per_parent = match.count
                output_per_child = match.pack(output)
                total_output_needed = output.quantity * quantity

                output_per_item = parent_sheet_per_item * child_sheet_per_parent * output_per_child
                items_needed = math.ceil(total_output_needed / output_per_item)
                runs_needed = items_needed * parent_sheet_per_item

                run_count = Quantity(sheet=runs_needed)
                item_count = Quantity(sheet=items_needed)
                total_area = runs_needed * match.parent.area

                estimate = Estimate(run_count=run_count, item_count=item_count)
                estimate.area = total_area
                
                return estimate
            else:
                return None

    def add_parent_sheet(self, width_value, length_value, size_uom, 
        padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, **kwargs):

        def within_bounds(a_val, a_unit, min_val, max_val, unit):
            return to_distance(min_val, unit) <= to_distance(a_val, a_unit) <= to_distance(max_val, unit)
        def to_distance(value, uom):
            return Distance(**{uom: value})

        if not within_bounds(width_value, size_uom, self.min_sheet_width, self.max_sheet_width, self.uom):
            raise ValueError("width must be within the range: %s - %s %s" %
                (self.min_sheet_width, self.max_sheet_width, self.uom))
        if not within_bounds(length_value, size_uom, self.min_sheet_length, self.max_sheet_length, self.uom):
            raise ValueError("length must be within the range: %s - %s %s" %
                (self.min_sheet_width, self.max_sheet_width, self.uom))

        parent = ParentSheet.objects.create(machine=self,
            width_value=width_value, length_value=length_value, size_uom=size_uom,
            padding_top=padding_top, padding_right=padding_right,
            padding_bottom=padding_bottom, padding_left=padding_left, **kwargs)

        return parent


class ParentSheet(Rectangle):
    machine = models.ForeignKey(SheetFedPressMachine, on_delete=models.CASCADE, 
        related_name='parent_sheets') 
    label = models.CharField(max_length=30, blank=True, null=True)
    padding_top = models.FloatField(default=0)
    padding_right = models.FloatField(default=0)
    padding_bottom = models.FloatField(default=0)
    padding_left = models.FloatField(default=0)

    @property
    def pack_width(self):
        return self.width_value - self.padding_x

    @property
    def pack_length(self):
        return self.length_value - self.padding_y

    @property
    def pack_size(self):
        unit = _inflect.plural(self.size_uom)
        return '%g x %g %s' % (self.pack_width, self.pack_length, unit)

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

    def add_child_sheet(self, width_value, length_value, size_uom, 
        margin_top=0, margin_right=0, margin_bottom=0, margin_left=0, **kwargs):

        if not self.within_bounds(width_value + margin_left + margin_right, 
                length_value + margin_top + margin_bottom, size_uom):
            raise ValueError("size must be within bounds: %s x %s %s" % 
                (self.width_value, self.length_value, self.size_uom))

        child = ChildSheet.objects.create(parent=self,
            width_value=width_value, length_value=length_value, size_uom=size_uom,
            margin_top=margin_top, margin_right=margin_right,
            margin_bottom=margin_bottom, margin_left=margin_left, **kwargs)
            
        return child

    def __str__(self):
        unit = _inflect.plural(self.size_uom)
        return '%g x %g %s' % (self.width_value, self.length_value, unit)


class ChildSheet(Rectangle):
    parent = models.ForeignKey(ParentSheet, 
        on_delete=models.CASCADE, related_name='child_sheets')
    label = models.CharField(max_length=30, blank=True, null=True)
    margin_top = models.FloatField(default=0)
    margin_right = models.FloatField(default=0)
    margin_bottom = models.FloatField(default=0)
    margin_left = models.FloatField(default=0)

    @property
    def has_bleed(self):
        return self.margin_top + self.margin_right + \
            self.margin_bottom + self.margin_left > 0

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
    def count(self):
        return self.parent.pack(self) 

    @classmethod
    def get_layout(cls, 
            parent_width, parent_length, parent_uom, 
            parent_padding_top, parent_padding_bottom,
            parent_padding_right, parent_padding_left,
            child_width, child_length, child_uom, 
            child_margin_top, child_margin_bottom,
            child_margin_right, child_margin_left,
            rotate=False):

        def __get_usage__(pw, pl, pu, cw, cl, cu, count):
            d_cw = Distance(**{cu: cw})
            d_cl = Distance(**{cu: cl})
            d_pw = Distance(**{pu: pw})
            d_pl = Distance(**{pu: pl})
            ca = d_cw.mm * d_cl.mm * count
            pa = d_pw.mm * d_pl.mm
            return (ca / pa)

        ppackw = parent_width - (parent_padding_left + parent_padding_right)
        ppackl = parent_length - (parent_padding_top + parent_padding_bottom)
        cpackw = child_width + (child_margin_left + child_margin_right)
        cpackl = child_length + (child_margin_top + child_margin_bottom)

        layout = Rectangle.binpacker(
            ppackw, ppackl, parent_uom,
            cpackw, cpackl, child_uom, rotate)

        count = len(layout) if layout is not None else 0
        usage = __get_usage__(ppackw, ppackl, parent_uom, 
            cpackw, cpackl, child_uom, count) if layout is not None else 0
        wastage = 1 - usage
        
        return layout, count, round(usage, 2), round(wastage, 2)

    def __str__(self):
        unit = _inflect.plural(self.size_uom)
        return '%g x %g %s' % (self.width_value, self.length_value, unit)