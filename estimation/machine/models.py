import math, copy
from django.db import models
from core.utils.shapes import Rectangle
from core.utils.measures import Measure, CostingMeasure, Quantity
from measurement.measures import Distance, Area
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from inventory.models import Item
from inventory.properties.models import Paper


class MachineManager(PolymorphicManager):
    def create_machine(self, **kwargs):
        mapping = {
            Machine.SHEET_FED_PRESS : SheetFedPressMachine,
            Machine.ROLL_FED_PRESS : RollFedPressMachine
        }
        type = kwargs.get('type', Machine.SHEET_FED_PRESS)
        clazz = mapping[type]
        machine = clazz.objects.create(**kwargs)
        return machine


class Machine(PolymorphicModel): 
    SHEET_FED_PRESS = 'SheetFedPressMachine'
    ROLL_FED_PRESS = 'RollFedPressMachine'
    TYPES = [
        (SHEET_FED_PRESS, 'Sheet-fed Press'),
        (ROLL_FED_PRESS, 'Roll-fed Press')
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

    # Get sheet layout given the following:
    # raw_material_layout - the layout of the raw material
    # final_material_layout - the layout of the final material after converting the raw material
    def get_sheet_layouts(self, raw_material_layout:Paper.Layout, 
            final_material_layout:Paper.Layout, rotate=False, **kwargs):
        layouts = self.get_layouts_meta(final_material_layout, raw_material_layout, 
            rotate, **kwargs)
        return layouts

    def get_layouts_meta(self, final_material_layout, raw_material_layout, rotate, **kwargs):
        # Implement this method
        pass


class RollFedPressMachine(PressMachine):
    min_sheet_width = models.FloatField(default=0)
    max_sheet_width = models.FloatField(default=0)
    min_sheet_breakpoint_length = models.FloatField(default=0)
    max_sheet_breakpoint_length = models.FloatField(default=0)
    make_ready_spoilage_length = models.FloatField(default=0)
    vertical_margin = models.FloatField(default=0)
    horizontal_margin = models.FloatField(default=0)
    uom = models.CharField(max_length=30, default='mm',
        choices=Measure.UNITS[Measure.DISTANCE])

    def _to_measurement(self, value):
        m = Distance(inch=0)
        if value is not None and self.uom is not None:
            m = Distance(**{self.uom: value})
        return m

    @property
    def margin_x_measurement(self):
        return self._to_measurement(self.horizontal_margin)

    @property
    def margin_y_measurement(self):
        return self._to_measurement(self.vertical_margin)

    @property
    def make_ready_spoilage_length_measurement(self):
        return self._to_measurement(self.make_ready_spoilage_length)

    @property
    def min_breakpoint_length_measurement(self):
        return self._to_measurement(self.min_sheet_breakpoint_length) 

    @property
    def max_breakpoint_length_measurement(self):
        return self._to_measurement(self.max_sheet_breakpoint_length) 

    @property
    def min_printable_width(self):
        return self.min_sheet_width - (self.horizontal_margin*2)

    @property
    def max_printable_width(self):
        return self.max_sheet_width - (self.horizontal_margin*2)

    @property
    def min_printable_width_measurement(self):
        return self._to_measurement(self.min_printable_width)

    @property
    def max_printable_width_measurement(self):
        return self._to_measurement(self.max_printable_width)

    def _validate_raw_material(self, material_layout):
        # returns width, length where length is always the longer dimension
        def _get_material_dimensions(material_layout):
            width, length = ((material_layout.width_measurement, material_layout.length_measurement)
                if material_layout.length > material_layout.width 
                else (material_layout.length_measurement, material_layout.width_measurement))
            return width, length

        width, length = _get_material_dimensions(material_layout)

        if length < self.min_breakpoint_length_measurement:
            raise ValueError('length of material cannot be lesser than the minimum breakpoint length.',
                length, 'vs.', self.min_breakpoint_length_measurement)

        if getattr(width, self.uom) < self.min_sheet_width:
            raise ValueError('width of material cannot be lesser than the minimum sheet width.',
                width, 'vs.', self.min_sheet_width)

        if getattr(width, self.uom) > self.max_sheet_width:
            raise ValueError('width of material cannot be greather than the maximum sheet width.',
                width, 'vs.', self.max_sheet_width)

    def get_layouts_meta(self, final_material_layout, raw_material_layout, rotate=False, 
            order_quantity=1, spoilage_rate=0, apply_breakpoint=False):

        if final_material_layout.width == 0:
            raise ValueError('Final material layout width should not be equal to zero')

        self._validate_raw_material(raw_material_layout)

        def _get_runsheet_layouts(quantity):
            def _get_runsheet_width(final_material_width):
                printable_width = raw_material_layout.width_measurement - (self.margin_x_measurement*2)
                count = printable_width / final_material_width
                return math.floor(count) * final_material_width

            def _create_layout(width, length, uom):
                layout = Rectangle.Layout(width=width, length=length, uom=uom)
                return layout

            quantity = float(quantity)
            runsheet_width_measurement = _get_runsheet_width(
                final_material_layout.total_width_measurement)
            runsheet_width = getattr(runsheet_width_measurement, self.uom)

            if runsheet_width == 0:
                return ValueError('Final sheet width does not fit within the printable area of the raw material.')
            
            runsheet_width = round(runsheet_width, 4)
            total_item_area_measurement = final_material_layout.area_measurement * quantity
            total_item_area = getattr(total_item_area_measurement, 'sq_%s' % self.uom)
            total_item_length = (round(total_item_area, 4) / runsheet_width)
            runsheet_length = total_item_length
            layouts = []

            if apply_breakpoint:
                if self.min_sheet_breakpoint_length > total_item_length:
                    runsheet_length = self.min_sheet_breakpoint_length
                elif total_item_length > self.max_sheet_breakpoint_length:
                    runsheet_length = self.max_sheet_breakpoint_length
                
                if total_item_length > runsheet_length:
                    remainder_length = total_item_length % runsheet_length
                    if remainder_length > 0:
                        if self.min_sheet_breakpoint_length > remainder_length:
                            remainder_length = self.min_sheet_breakpoint_length
                        remainder_rect = _create_layout(runsheet_width, 
                            remainder_length, self.uom)
                        remainder_layout = Rectangle.get_layout(remainder_rect, 
                            final_material_layout,
                            False, 'Runsheet-to-cutsheet-remainder')
                        layouts.append(remainder_layout)

            runsheet_layout = _create_layout(runsheet_width, runsheet_length, self.uom)
            layout = Rectangle.get_layout(runsheet_layout, final_material_layout, 
                False, 'Runsheet-to-cutsheet')
            layouts.insert(0, layout)
            return layouts     

        quantity = order_quantity * (1+(spoilage_rate/100))
        runsheet_to_final_layouts = _get_runsheet_layouts(quantity)
        
        return runsheet_to_final_layouts


class SheetFedPressMachine(PressMachine):
    min_sheet_length = models.FloatField(default=0)
    max_sheet_length = models.FloatField(default=0)
    min_sheet_width = models.FloatField(default=0)
    max_sheet_width = models.FloatField(default=0)
    uom = models.CharField(max_length=30, default='mm',
        choices=Measure.UNITS[Measure.DISTANCE])
    
    def get_layouts_meta(self, final_material_layout, raw_material_layout, rotate=False):
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
                elif machine_max_length.mm > halved_input_length.mm > material_length.mm:
                    runsheet_length_base = _get_attr(machine_max_length, uom)
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
                elif machine_max_width.mm > halved_input_width.mm > material_width.mm:
                    runsheet_width_base = _get_attr(machine_max_width, uom)
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
            raw_material_layout.width, raw_material_layout.length, raw_material_layout.uom, 
            final_material_layout.width, final_material_layout.length, final_material_layout.uom)
        parent_to_child_layout_meta = ChildSheet.get_layout(
            item_to_parent_layout_meta.rect, final_material_layout, rotate, 'Runsheet-to-cutsheet')
        child_count = item_to_parent_layout_meta.count * parent_to_child_layout_meta.count

        rotated_item_to_parent_layout_meta = _get_parentsheet_layout_meta(
            raw_material_layout.length, raw_material_layout.width, raw_material_layout.uom,
            final_material_layout.width, final_material_layout.length, final_material_layout.uom)
        rotated_parent_to_child_layout_meta = ChildSheet.get_layout(
            rotated_item_to_parent_layout_meta.rect, final_material_layout, rotate, 'Runsheet-to-cutsheet')
        rotated_child_count = rotated_item_to_parent_layout_meta.count * rotated_parent_to_child_layout_meta.count

        return_layouts_meta = [item_to_parent_layout_meta, parent_to_child_layout_meta]

        if child_count < rotated_child_count:
            return_layouts_meta = [rotated_item_to_parent_layout_meta, 
                rotated_parent_to_child_layout_meta]

        return return_layouts_meta


class ParentSheet:
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


class ChildSheet:
    class Layout(Rectangle.Layout):
        def __init__(self, margin_top=0, margin_right=0, 
                margin_bottom=0, margin_left=0, **kwargs):
            super().__init__(**kwargs)
            self.margin_top = margin_top
            self.margin_right = margin_right
            self.margin_bottom = margin_bottom
            self.margin_left = margin_left
        
        @property
        def total_width_measurement(self):
            return self.width_measurement + self._to_measurement(self.margin_x)

        @property
        def total_length_measurement(self):
            return self.length_measurement + self._to_measurement(self.margin_y)

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