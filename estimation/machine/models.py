import math, copy
from django.db import models
from core.utils.shapes import Rectangle
from core.utils.measures import Measure, CostingMeasure, Quantity
from measurement.measures import Distance, Area
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from inventory.models import Item
from inventory.properties.models import Paper
import inflect

_inflect = inflect.engine()


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

    material_type = Item.OTHER

    def estimate(self, **kwargs):
        pass

    @property
    def costing_measures(self):
        return [x[0] for x in Item.get_costing_measure_choices(self.material_type)]

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
    material_type = Item.PAPER


class SheetFedPressMachine(PressMachine):
    min_sheet_length = models.FloatField(default=0)
    max_sheet_length = models.FloatField(default=0)
    min_sheet_width = models.FloatField(default=0)
    max_sheet_width = models.FloatField(default=0)
    uom = models.CharField(max_length=30, default='mm',
        choices=Measure.UNITS[Measure.DISTANCE])
    
    def get_layouts_meta(self, material_layout, item_layout, rotate=False):
        # Dirty workaround for the floating point-number lossy 
        # implementation in python-measurements package
        def _is_gte(x, y):
            return x.mm > y.mm or math.isclose(x.mm, y.mm)

        def _get_attr(obj, attr):
            return getattr(obj, attr) if hasattr(obj, attr) else 0

        def _to_distance(value, uom):
            return Distance(**{uom: value})

        def _get_length(length, uom, m_length_value=0, m_length_uom='inch'):
            runsheet_length_base = length
            input_length = _to_distance(length, uom)
            machine_max_length = _to_distance(self.max_sheet_length, self.uom)
            machine_min_length = _to_distance(self.min_sheet_length, self.uom)
            material_length = _to_distance(m_length_value, m_length_uom)

            if input_length.mm > machine_max_length.mm:
                halved_input_length = input_length / 2
                if _is_gte(material_length, halved_input_length):
                    runsheet_length_base = _get_attr(material_length, uom)
                elif _is_gte(machine_max_length, halved_input_length) and \
                        _is_gte(halved_input_length, machine_min_length):
                    runsheet_length_base = length / 2
                elif machine_min_length.mm > halved_input_length.mm > material_length.mm:
                    runsheet_length_base = _get_attr(machine_min_length, uom)
                else:
                    runsheet_length_base = _get_length(length/2, uom)
                    
            return runsheet_length_base

        def _get_width(width, uom, rs_length_value=0, rs_length_uom='inch',
                m_width_value=0, m_width_uom='inch'):
            runsheet_width_base = width
            runsheet_length = _to_distance(rs_length_value, rs_length_uom)
            input_width = _to_distance(width, uom)
            machine_max_width = _to_distance(self.max_sheet_width, self.uom)
            machine_min_width = _to_distance(self.min_sheet_width, self.uom)
            material_width = _to_distance(m_width_value, m_width_uom)

            if input_width.mm > machine_max_width.mm:
                halved_input_width = input_width / 2
                input_width_less_rs_length = input_width - runsheet_length
                if _is_gte(material_width, halved_input_width):
                    runsheet_width_base = _get_attr(material_width, uom)
                elif _is_gte(machine_max_width, halved_input_width) and \
                        _is_gte(halved_input_width, machine_min_width) and \
                        input_width_less_rs_length.mm > halved_input_width.mm:
                    runsheet_width_base = width / 2
                elif rotate and input_width_less_rs_length.mm > 0 and \
                        _is_gte(machine_max_width, input_width_less_rs_length) and \
                        _is_gte(input_width_less_rs_length, machine_min_width):
                    runsheet_width_base = width - rs_length_value
                elif machine_min_width.mm > halved_input_width.mm > material_width.mm:
                    runsheet_width_base = _get_attr(machine_min_width, uom)
                else:
                    runsheet_width_base = _get_width(width/2, uom)
                    
            return runsheet_width_base
        
        def _create_parentsheet_layout(width, length, uom):
            return ParentSheet.Layout(width=width, length=length, uom=uom)

        def _get_parentsheet_layout_meta(item_width, item_length, item_uom, 
                material_width, material_length, material_uom):
            rs_length = _get_length(item_length, item_uom, material_length, material_uom)
            rs_width = _get_width(item_width, item_uom, rs_length, item_uom, 
                material_width, material_uom)
            item_layout = Rectangle.Layout(width=item_width, length=item_length, uom=item_uom)
            parent_layout = _create_parentsheet_layout(rs_width, rs_length, item_uom)
            layout_meta = ParentSheet.get_layout(item_layout, parent_layout, rotate, 'Parent-to-runsheet')
            return layout_meta

        def _rotate_material(child_layout):
            if child_layout is not None:
                return ChildSheet.Layout(
                    margin_top=child_layout.margin_right, margin_right=child_layout.margin_bottom,
                    margin_bottom=child_layout.margin_left, margin_left=child_layout.margin_top,
                    width=child_layout.length, length=child_layout.width, uom=child_layout.uom, 
                    is_rotated=True)

        item_to_parent_layout_meta = _get_parentsheet_layout_meta(
            item_layout.width, item_layout.length, item_layout.uom, 
            material_layout.width, material_layout.length, material_layout.uom)
        parent_to_child_layout_meta = ChildSheet.get_layout(
            item_to_parent_layout_meta.rect, material_layout, rotate, 'Runsheet-to-cutsheet')
        child_count = item_to_parent_layout_meta.count * parent_to_child_layout_meta.count

        rotated_item_to_parent_layout_meta = _get_parentsheet_layout_meta(
            item_layout.length, item_layout.width, item_layout.uom,
            material_layout.width, material_layout.length, material_layout.uom)
        rotated_parent_to_child_layout_meta = ChildSheet.get_layout(
            rotated_item_to_parent_layout_meta.rect, material_layout, rotate, 'Runsheet-to-cutsheet')
        rotated_child_count = rotated_item_to_parent_layout_meta.count * rotated_parent_to_child_layout_meta.count

        return_layouts_meta = [item_to_parent_layout_meta, parent_to_child_layout_meta]

        if child_count < rotated_child_count:
            return_layouts_meta = [rotated_item_to_parent_layout_meta, 
                rotated_parent_to_child_layout_meta]

        return return_layouts_meta


    def get_sheet_layouts(self, material_layout:Paper.Layout, item_layout:Paper.Layout,
            rotate=False):
        layouts = self.get_layouts_meta(material_layout, item_layout, rotate)
        return layouts
                

    def estimate(self, material, quantity, rotate=False):
        if material.type == Item.PAPER:
            layouts = self.get_sheet_layouts(material.layout, 
                material.item_properties.layout, rotate)

            if layouts is not None and len(layouts) == 2:
                # Item refers to the stock / raw material
                # Parent refers to the press running sheet that the machine accepts
                # Child refers to the divided parent sheets
                # Output refers to the divided child sheets. It's also the final size.
                item_to_parent_layout_meta = layouts[0]
                parent_to_child_layout_meta = layouts[1]

                parent_sheet_per_item = item_to_parent_layout_meta.count
                child_sheet_per_parent = parent_to_child_layout_meta.count
                total_output_needed = material.quantity * quantity

                output_per_item = parent_sheet_per_item * child_sheet_per_parent 
                items_needed = math.ceil(total_output_needed / output_per_item)
                runs_needed = items_needed * parent_sheet_per_item

                run_count = Quantity(sheet=runs_needed)
                parent_layout = item_to_parent_layout_meta.rect
                parent_area = Area(**{'sq_%s' % parent_layout.uom: parent_layout.area})
                total_area = runs_needed * parent_area
                
                return {
                    CostingMeasure.AREA: total_area,
                    CostingMeasure.QUANTITY: run_count
                }
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
    class Layout(Rectangle.Layout):
        def __init__(self, padding_top=0, padding_right=0, 
                padding_bottom=0, padding_left=0, **kwargs):
            super().__init__(**kwargs)
            self.padding_top = padding_top
            self.padding_right = padding_right
            self.padding_bottom = padding_bottom
            self.padding_left = padding_left
        
        @property
        def padding_x(self):
            return self.padding_right + self.padding_left

        @property
        def padding_y(self):
            return self.padding_top + self.padding_bottom

        def get_pack_size_as_bin(self):
            return (self.width - self.padding_x), \
                (self.length - self.padding_y), self.uom
        
        def get_pack_size_as_rect(self):
            return self.width, self.length, self.uom

    machine = models.ForeignKey(SheetFedPressMachine, on_delete=models.CASCADE, 
        related_name='parent_sheets') 
    label = models.CharField(max_length=30, blank=True, null=True)
    padding_top = models.FloatField(default=0)
    padding_right = models.FloatField(default=0)
    padding_bottom = models.FloatField(default=0)
    padding_left = models.FloatField(default=0)

    @property
    def layout(self):
        return ParentSheet.Layout(width=self.width_value, 
            length=self.length_value, uom=self.size_uom, 
            padding_top=self.padding_top, padding_right=self.padding_right,
            padding_bottom=self.padding_bottom, padding_left=self.padding_left)

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

    # Returns the following:
    # layouts, count, usage, wastage, indices of rotated rectangles
    @classmethod
    def get_layout(cls, rect_layout:Rectangle, parent_layout:'ParentSheet.Layout', 
            rotate=False, name=None):
        layouts = []
        layout_meta = Rectangle.get_layout(
            rect_layout, parent_layout, rotate, name)

        for layout in layout_meta.layouts:
            parent = copy.copy(parent_layout)
            parent.i = layout.i 
            parent.x = layout.x 
            parent.y = layout.y 
            if layout.is_rotated:
                parent.is_rotated = layout.is_rotated
                temp_width = parent.width
                parent.width = parent.length
                parent.length = temp_width
                temp_padding = parent.padding_top
                parent.padding_top = parent.padding_right
                parent.padding_right = parent.padding_bottom
                parent.padding_bottom = parent.padding_left
                parent.padding_left = temp_padding
            layouts.append(parent)

        layout_meta.layouts = layouts

        return layout_meta

    def __str__(self):
        unit = _inflect.plural(self.size_uom)
        return '%g x %g %s' % (self.width_value, self.length_value, unit)


class ChildSheet(Rectangle):
    class Layout(Rectangle.Layout):
        def __init__(self, margin_top=0, margin_right=0, 
                margin_bottom=0, margin_left=0, **kwargs):
            super().__init__(**kwargs)
            self.margin_top = margin_top
            self.margin_right = margin_right
            self.margin_bottom = margin_bottom
            self.margin_left = margin_left
        
        @property
        def margin_x(self):
            return self.margin_right + self.margin_left

        @property
        def margin_y(self):
            return self.margin_top + self.margin_bottom

        def get_pack_size_as_bin(self):
            return self.width, self.length, self.uom
        
        def get_pack_size_as_rect(self):
            return self.width + self.margin_x, \
                self.length + self.margin_y, self.uom

    parent = models.ForeignKey(ParentSheet, 
        on_delete=models.CASCADE, related_name='child_sheets')
    label = models.CharField(max_length=30, blank=True, null=True)
    margin_top = models.FloatField(default=0)
    margin_right = models.FloatField(default=0)
    margin_bottom = models.FloatField(default=0)
    margin_left = models.FloatField(default=0)

    @property
    def layout(self):
        return ChildSheet.Layout(width=self.width_value, 
            length=self.length_value, uom=self.size_uom,
            margin_top=self.margin_top, margin_right=self.margin_right,
            margin_bottom=self.margin_bottom, margin_left=self.margin_left)

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

        
    # Returns the following:
    # layouts, count, usage, wastage, indices of rotated rectangles
    @classmethod
    def get_layout(cls, parent_layout:ParentSheet.Layout,
            child_layout:'ChildSheet.Layout', rotate=False, 
            name='Parent-to-cutsheet'):
        layouts = []
        layout_meta = Rectangle.get_layout(
            parent_layout, child_layout, rotate, name)

        for layout in layout_meta.layouts:
            child = copy.copy(child_layout)
            child.i = layout.i 
            child.x = layout.x 
            child.y = layout.y 
            if layout.is_rotated:
                child.is_rotated = layout.is_rotated
                child.width = layout.width 
                child.length = layout.length
                if type(layout).__qualname__ == 'ChildSheet.Layout':
                    temp = child.margin_top
                    child.margin_top = child.margin_right
                    child.margin_right = child.margin_bottom
                    child.margin_bottom = child.margin_left
                    child.margin_left = temp
            layouts.append(child)

        layout_meta.layouts = layouts

        return layout_meta

    def __str__(self):
        unit = _inflect.plural(self.size_uom)
        return '%g x %g %s' % (self.width_value, self.length_value, unit)