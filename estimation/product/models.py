import math
from django.db import models
from core.utils.measures import Quantity, CostingMeasure
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.machine.models import Machine, ChildSheet
from estimation.exceptions import MaterialTypeMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from djmoney.models.fields import MoneyField


class Product(models.Model):
    name = models.CharField(max_length=20, null=True)
    quantity = models.IntegerField(default=1)


class Component(models.Model):
    name = models.CharField(max_length=20, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    machine = models.OneToOneField(Machine, on_delete=models.SET_NULL,
        null=True, related_name='component')
    quantity = models.IntegerField(default=1)

    @property
    def total_material_quantity(self):
        return self.materials.count() * self.quantity


class MaterialManager(PolymorphicManager):

    @classmethod
    def get_class(cls, type):
        mapping = {
            Item.TAPE: TapeMaterial,
            Item.LINE: LineMaterial,
            Item.PAPER: PaperMaterial,
            Item.PANEL: PanelMaterial,
            Item.LIQUID: LiquidMaterial,
            Item.OTHER: Material
        }
        clazz = mapping.get(type, Material)
        return clazz

    def create_material(self, component, type, item, name=None, **kwargs):
        if item.type != type:
            raise MaterialTypeMismatch(item.type, type)
        clazz = MaterialManager.get_class(type)
        material = clazz.objects.create(component=component, name=name, 
            item=item, **kwargs)
        return material


class Material(PolymorphicModel, Shape):

    class Estimate:
        def __init__(self, order_quantity, material_quantity, 
                spoilage_rate=0, layouts_meta=None):
            self.order_quantity = order_quantity
            self.material_quantity = material_quantity
            self.spoilage_rate = spoilage_rate
            self.layouts_meta = layouts_meta 
        
        @property
        def layouts(self):
            pass

        @property
        def estimated_stock_quantity(self):
            output_per_item = max(self.output_per_item, 1)
            total_material_quantity = self.total_material_measures.get(CostingMeasure.QUANTITY)
            total_material = total_material_quantity.value if total_material_quantity is not None else 0
            return math.ceil(total_material / output_per_item)

        @property
        def estimated_spoilage_quantity(self):
            spoilage_multiplier = (self.spoilage_rate / 100)
            return math.ceil(self.estimated_stock_quantity * spoilage_multiplier)

        @property
        def estimated_total_quantity(self):
            return self.estimated_stock_quantity + self.estimated_spoilage_quantity

        @property
        def raw_material_measures(self):
            value = self.estimated_total_quantity
            return {CostingMeasure.QUANTITY: Quantity(pc=value)}

        @property
        def set_material_measures(self):
            value = self.material_quantity
            return {CostingMeasure.QUANTITY: Quantity(pc=value)}
        
        @property
        def total_material_measures(self):
            total_material = self.order_quantity * self.material_quantity
            return {CostingMeasure.QUANTITY: Quantity(pc=total_material)}

        @property
        def machine_run_measures(self):
            pass

        @property
        def output_per_item(self):
            return 1

    objects = MaterialManager()
    component = models.ForeignKey(Component, on_delete=models.CASCADE,
        related_name='materials', null=True, blank=True)
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=True)
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, 
        related_name='materials')

    price = MoneyField(default=0, max_digits=14, decimal_places=2, 
        default_currency='PHP')
    spoilage_rate = models.FloatField(default=0)

    @classmethod
    def get_class(cls, type):
        return cls.objects.get_class(type)

    @property
    def quantity(self):
        quantity = 1
        if self.component is not None:
            quantity = self.component.quantity
        return quantity

    @property
    def item_properties(self):
        return self.item.properties

    def estimate(self, quantity):
        pass
        

class TapeMaterial(Material, Tape):
    type = Item.TAPE


class LineMaterial(Material, Line):
    type = Item.LINE


class PaperMaterial(Material, Paper):
    class Estimate(Material.Estimate):

        @property
        def layouts(self):
            layouts = {
                'parent_sheet': None,
                'run_sheet': None,
                'final_sheet': None
            }

            if self.layouts_meta is not None:
                layouts_count = len(self.layouts_meta)

                if layouts_count == 2:
                    parent_to_runsheet = self.layouts_meta[0]
                    runsheet_to_finalsheet = self.layouts_meta[1]

                    layouts['parent_sheet'] = parent_to_runsheet.bin
                    layouts['run_sheet'] = parent_to_runsheet.rect 
                    layouts['final_sheet'] = runsheet_to_finalsheet.rect

                elif layouts_count == 1:
                    parent_to_finalsheet = self.layouts_meta[0]

                    layouts['parent_sheet'] = parent_to_finalsheet.bin
                    layouts['final_sheet'] = parent_to_finalsheet.rect

            return layouts

        @property
        def raw_material_measures(self):
            measures = super().raw_material_measures
            raw_material = self.layouts.get('parent_sheet')
            quantity = measures[CostingMeasure.QUANTITY]

            add = self._get_additional_measures(raw_material, quantity.value)
            measures.update(add)

            return measures

        @property
        def set_material_measures(self):
            measures = super().set_material_measures
            set_material = self.layouts.get('final_sheet')
            quantity = measures[CostingMeasure.QUANTITY]

            add = self._get_additional_measures(set_material, quantity.value)
            measures.update(add)

            return measures
        
        @property
        def total_material_measures(self):
            measures = super().total_material_measures
            set_material = self.layouts.get('final_sheet')
            quantity = measures[CostingMeasure.QUANTITY]

            add = self._get_additional_measures(set_material, quantity.value)
            measures.update(add)

            return measures

        @property
        def machine_run_measures(self):
            machine_run_quantity = 0

            if self.layouts_meta is not None:
                layouts_count = len(self.layouts_meta)

                if layouts_count == 2:
                    item_to_parent_layout_meta = self.layouts_meta[0]
                    parent_sheet_per_item = item_to_parent_layout_meta.count

                    machine_run_quantity = math.ceil(self.estimated_total_quantity * parent_sheet_per_item)

                elif layouts_count == 1:
                    item_to_child_layout_meta = self.layouts_meta[0]
                    child_sheet_per_item = item_to_child_layout_meta.count

                    machine_run_quantity = math.ceil(self.estimated_total_quantity * child_sheet_per_item)
            
            run_sheet = self.layouts.get('run_sheet')
            measures = {CostingMeasure.QUANTITY: Quantity(pc=machine_run_quantity)}
            add = self._get_additional_measures(run_sheet, machine_run_quantity)
            measures.update(add)
            
            return measures

        @property
        def raw_to_running_cut(self):
            cut_count = 0

            if self.layouts_meta is not None:
                layouts_count = len(self.layouts_meta)

                if layouts_count == 2:
                    item_to_parent_layout_meta = self.layouts_meta[0]
                    cut_count = item_to_parent_layout_meta.cut_count

            return cut_count
        
        @property
        def running_to_final_cut(self):
            cut_count = 0
            
            if self.layouts_meta is not None:
                layouts_count = len(self.layouts_meta)

                if layouts_count == 2:
                    parent_to_child_layout_meta = self.layouts_meta[1]
                    cut_count = parent_to_child_layout_meta.cut_count
            
            return cut_count
        
        @property
        def raw_to_final_cut(self):
            cut_count = 0

            if self.layouts_meta is not None:
                layouts_count = len(self.layouts_meta)

                if layouts_count == 1:
                    item_to_child_layout_meta = self.layouts_meta[0]
                    cut_count = item_to_child_layout_meta.cut_count

            return cut_count

        @property
        def output_per_item(self):
            output_per_item = 0

            if self.layouts_meta is not None:
                layouts_count = len(self.layouts_meta)

                if layouts_count == 2:
                    item_to_parent_layout_meta = self.layouts_meta[0]
                    parent_to_child_layout_meta = self.layouts_meta[1]

                    if item_to_parent_layout_meta.name == 'Parent-to-runsheet' and \
                            parent_to_child_layout_meta.name == 'Runsheet-to-cutsheet':
                        parent_sheet_per_item = item_to_parent_layout_meta.count
                        child_sheet_per_parent = parent_to_child_layout_meta.count
                        output_per_item = parent_sheet_per_item * child_sheet_per_parent

                elif layouts_count == 1:
                    item_to_child_layout_meta = self.layouts_meta[0]

                    if item_to_child_layout_meta.name == 'Parent-to-cutsheet':
                        output_per_item = item_to_child_layout_meta.count

            return output_per_item

        def _get_additional_measures(self, layout, quantity=0):
            measures = {}
            if layout is not None:
                measures = {
                    CostingMeasure.AREA: layout.area_measurement * quantity,
                    CostingMeasure.PERIMETER: layout.perimeter_measurement * quantity
                }
            return measures

    type = Item.PAPER

    def estimate(self, quantity, spoilage_rate=0, rotate=True):
        estimate = None

        if self.item is not None:
            layouts = []
            machine = self.component.machine
            if self.component is not None and machine is not None:
                layouts = machine.get_sheet_layouts(self.item_properties.layout, self.layout, rotate)
            else:
                layouts = [ChildSheet.get_layout(self.item_properties.layout, self.layout, rotate)]
       
            estimate = PaperMaterial.Estimate(quantity, self.component.quantity,
                spoilage_rate, layouts)
        
        return estimate
 
class PanelMaterial(Material, Panel):
    type = Item.PANEL


class LiquidMaterial(Material, Liquid):
    type = Item.LIQUID