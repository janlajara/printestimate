import math
from django.db import models
from core.utils.measures import Quantity, CostingMeasure
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.metaproduct.models import MetaEstimateVariable
from estimation.process.models import ActivityExpense, Speed
from estimation.template.models import ProductTemplate, ComponentTemplate
from estimation.machine.models import Machine, ChildSheet
from estimation.exceptions import MaterialTypeMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from djmoney.models.fields import MoneyField


class ProductEstimateManager(models.Manager):

    def create_product_estimate(self, product_template, quantities):
        product_estimate = ProductEstimate.objects.create(product_template=product_template)
        for quantity in quantities:
            EstimateQuantity.objects.create(product_estimate=product_estimate, quantity=quantity)

        product = Product.objects.create(name=product_template.name, product_estimate=product_estimate)
        
        for component_template in product_template.component_templates.all():
            component = Component.objects.create_component(component_template, product)

        return product_estimate


class ProductEstimate(models.Model):
    objects = ProductEstimateManager()
    product_template = models.ForeignKey(ProductTemplate, null=True, on_delete=models.SET_NULL)


class EstimateQuantity(models.Model):
    product_estimate = models.ForeignKey(ProductEstimate, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Product(models.Model):
    name = models.CharField(max_length=20, null=True)
    product_estimate = models.OneToOneField(ProductEstimate, on_delete=models.CASCADE,
        null=True, blank=True)


class ComponentManager(models.Manager):
    def create_component(self, component_template, product):
        name = component_template.name
        machine = component_template.machine_option.machine if \
            component_template.machine_option is not None and \
            component_template.machine_option.machine is not None else None
        component = Component.objects.create(name=name, 
            component_template=component_template,
            machine=machine, product=product,
            quantity=component_template.quantity)

        for material_template in component_template.material_templates.all():
            material = Material.objects.create_material(component, 
                material_template.type, material_template.item,
                material_template.label, material_template.item.price,
                **component_template.prop_args)
        
        return component


class Component(models.Model):
    objects = ComponentManager()
    name = models.CharField(max_length=20, null=True)
    component_template = models.ForeignKey(ComponentTemplate, 
        on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
        related_name='components')
    machine = models.OneToOneField(Machine, on_delete=models.SET_NULL,
        null=True, related_name='component')
    quantity = models.IntegerField(default=1)


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

    def create_material(self, component, type, item, name=None, price=0, **kwargs):
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
    def label(self):
        return '%s %s' % (self.item.name, self)

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
    type = Item.PAPER

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
                    layouts = {
                        'parent_sheet': parent_to_runsheet.bin,
                        'run_sheet': parent_to_runsheet.rect,
                        'final_sheet': runsheet_to_finalsheet.rect
                    }

                elif layouts_count == 1:
                    parent_to_finalsheet = self.layouts_meta[0]
                    layouts = {
                        'parent_sheet': parent_to_finalsheet.bin,
                        'run_sheet': parent_to_finalsheet.rect,
                        'final_sheet': parent_to_finalsheet.rect
                    }

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


class ServiceManager(models.Manager):
    def create_service(self, service_template, product):
        name = service_template.name
        sequence = service_template.sequence
        costing_measure = service_template.costing_measure
        estimate_variable_type = service_template.estimate_variable_type

        component = None
        component_template = service_template.component_template
        if component_template is not None:
            component = product.components.get(component_template__pk=component_template.pk)

        service = Service.objects.create(name=name, product=product, 
            sequence=sequence, component=component, costing_measure=costing_measure,
            estimate_variable_type=estimate_variable_type)

        return service
        

class Service(models.Model):
    name = models.CharField(max_length=50, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.SET_NULL, 
        null=True, blank=True)
    sequence = models.IntegerField(default=1)
    costing_measure = models.CharField(max_length=15, 
        choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)
    estimate_variable_type = models.CharField(
        choices=MetaEstimateVariable.TYPE_CHOICES,
        max_length=30, blank=True, null=True)


class OperationEstimate(models.Model):
    name = models.CharField(max_length=50, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL,
        null=True, blank=True)


class ActivityEstimate(models.Model):
    name = models.CharField(max_length=50, null=True)
    operation_estimate = models.ForeignKey(OperationEstimate, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    measure_unit = models.CharField(max_length=20, blank=True, null=True)
    notes = models.CharField(max_length=20, blank=True, null=True)


class SpeedEstimate(Speed):
    activity_estimate = models.OneToOneField(ActivityEstimate, on_delete=models.CASCADE)


class ActivityExpenseEstimate(models.Model):
    name = models.CharField(max_length=50, null=True)
    activity_estimate = models.ForeignKey(ActivityEstimate, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=ActivityExpense.TYPES)
    rate = MoneyField(default=0, max_digits=14, decimal_places=2, 
        default_currency='PHP')

    @property
    def uom(self):
        uom = None
        if self.type == ActivityExpense.HOUR_BASED:
            uom = 'hr'
        elif self.type == ActivityExpense.MEASURE_BASED:
            uom = self.activity_estimate.measure_unit
        return uom

    @property
    def rate_label(self):
        label = self.rate
        if self.type == ActivityExpense.HOUR_BASED or self.type == ActivityExpense.MEASURE_BASED:
            label = '%s / %s' % (self.rate, self.uom)
        return label
        

