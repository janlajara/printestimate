import math
from django.db import models
from django_measurement.models import MeasurementField
from core.utils.measures import Quantity, CostingMeasure, Measure
from measurement.measures import Time
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.metaproduct.models import MetaEstimateVariable
from estimation.process.models import ActivityExpense, Speed
from estimation.template.models import ProductTemplate, ComponentTemplate
from estimation.machine.models import Machine, ChildSheet
from estimation.exceptions import MaterialTypeMismatch, MeasurementMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from djmoney.models.fields import MoneyField



class ProductEstimateManager(models.Manager):

    def create_product_estimate(self, product_template, quantities=None):
        product_estimate = ProductEstimate.objects.create(product_template=product_template)
        if quantities is not None:
            for quantity in quantities:
                EstimateQuantity.objects.create(product_estimate=product_estimate, quantity=quantity)

        product = Product.objects.create_product(product_template, product_estimate)

        return product_estimate


class ProductEstimate(models.Model):
    objects = ProductEstimateManager()
    product_template = models.ForeignKey(ProductTemplate, null=True, on_delete=models.SET_NULL)


class EstimateQuantity(models.Model):
    product_estimate = models.ForeignKey(ProductEstimate, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class ProductManager(models.Manager):
    def create_product(self, product_template, product_estimate=None):
        product = Product.objects.create(name=product_template.name, 
            product_estimate=product_estimate)
        components_map = {}

        for component_template in product_template.component_templates.all():
            component = Component.objects.create_component(component_template, product)
            components_map[component_template.pk] = component
    
        for service_template in product_template.service_templates.all():
            component = None
            if service_template.component_template is not None:
                component = components_map.get(service_template.component_template.pk, None)

            service = Service.objects.create_service(service_template, product, component)


class Product(models.Model):
    objects = ProductManager()
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
            machine=machine, product=product,
            quantity=component_template.quantity)

        for material_template in component_template.material_templates.all():
            material = Material.objects.create_material(component, 
                material_template.type, material_template.item,
                material_template.item.price, **component_template.prop_args)
        
        return component


class Component(models.Model):
    objects = ComponentManager()
    name = models.CharField(max_length=20, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
        related_name='components')
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL,
        null=True)
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

    def create_material(self, component, type, item, price=0, **kwargs):
        if item.type != type:
            raise MaterialTypeMismatch(item.type, type)
        clazz = MaterialManager.get_class(type)
        material = clazz.objects.create(component=component, 
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

        @property
        def costing_measurements_map(self):
            return {
                MetaEstimateVariable.RAW_MATERIAL: self.raw_material_measures,
                MetaEstimateVariable.SET_MATERIAL: self.set_material_measures,
                MetaEstimateVariable.TOTAL_MATERIAL: self.total_material_measures,
                MetaEstimateVariable.MACHINE_RUN: self.machine_run_measures
            }

    objects = MaterialManager()
    component = models.ForeignKey(Component, on_delete=models.CASCADE,
        related_name='materials', null=True, blank=True)
    material_id = models.AutoField(primary_key=True)
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
        def raw_to_running_measures(self):
            return {CostingMeasure.QUANTITY: Quantity(count=self.raw_to_running_cut)}

        @property
        def running_to_final_measures(self):
            return {CostingMeasure.QUANTITY: Quantity(count=self.running_to_final_cut)}

        @property
        def raw_to_final_measures(self):
            return {CostingMeasure.QUANTITY: Quantity(count=self.raw_to_final_cut)}

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

        @property
        def costing_measurements_map(self):
            map = super().costing_measurements_map
            to_add = {
                MetaEstimateVariable.RAW_TO_RUNNING_CUT: self.raw_to_running_measures,
                MetaEstimateVariable.RUNNING_TO_FINAL_CUT: self.running_to_final_measures,
                MetaEstimateVariable.RAW_TO_FINAL_CUT: self.raw_to_final_measures
            }
            map.update(to_add)
            return map

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
    def create_service(self, service_template, product, component=None):
        name = service_template.name
        sequence = service_template.sequence
        costing_measure = service_template.costing_measure
        estimate_variable_type = service_template.estimate_variable_type

        service = Service.objects.create(name=name, product=product, 
            sequence=sequence, component=component, costing_measure=costing_measure,
            estimate_variable_type=estimate_variable_type)

        component_materials = component.materials.all()

        for component_material in component_materials:
            for operation_template in service_template.operation_templates.all():
                OperationEstimate.objects.create_operation_estimate(
                    operation_template, service, component_material)

        return service
        

class Service(models.Model):
    class Estimate:
        def __init__(self, order_quantity, operation_estimates):
            self.order_quantity = order_quantity
            self.operation_estimates = operation_estimates

    objects = ServiceManager()
    name = models.CharField(max_length=50, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
        related_name='services')
    component = models.ForeignKey(Component, on_delete=models.SET_NULL, 
        null=True, blank=True)
    sequence = models.IntegerField(default=1)
    costing_measure = models.CharField(max_length=15, 
        choices=CostingMeasure.TYPES, 
        default=CostingMeasure.QUANTITY)
    estimate_variable_type = models.CharField(
        choices=MetaEstimateVariable.TYPE_CHOICES,
        max_length=30, blank=True, null=True)

    def estimate(self, order_quantity):
        def _get_costing_measurement(material, quantity):
            if material is not None and self.estimate_variable_type is not None:
                material_estimate = material.estimate(quantity)
                measures_mapping = material_estimate.costing_measurements_map                
                measures = measures_mapping.get(self.estimate_variable_type)
                if measures is not None:
                    result = measures.get(self.costing_measure, None)
                    return result

        def _get_activity_expense_estimates(costing_measurement, 
                duration, activity_expense_estimates):
            results = []
            for activity_expense_estimate in activity_expense_estimates:
                aee = ActivityExpenseEstimate.Estimate(
                    activity_expense_estimate.name,
                    activity_expense_estimate.uom, 
                    activity_expense_estimate.type,
                    activity_expense_estimate.rate, 
                    activity_expense_estimate.rate_label,
                    costing_measurement, duration)
                results.append(aee)
            return results

        def _get_activity_estimates(costing_measurement, activity_estimates):
            results = []
            for activity_estimate in activity_estimates:
                duration = activity_estimate.get_duration(costing_measurement)
                activity_expense_estimates = _get_activity_expense_estimates(
                    costing_measurement, duration, 
                    activity_estimate.activity_expense_estimates.all())
                ae = ActivityEstimate.Estimate(activity_estimate.name,
                    activity_estimate.notes, activity_expense_estimates)
                results.append(ae)
            return results

        def _get_operation_estimates(material, quantity, operation_estimates):
            costing_measurement = _get_costing_measurement(material, quantity)
            results = []
            for operation_estimate in operation_estimates:
                activity_estimates = _get_activity_estimates(
                    costing_measurement, operation_estimate.activity_estimates.all())
                oe = OperationEstimate.Estimate(operation_estimate.name, activity_estimates)
                results.append(oe)
            return results

        operation_estimates = []
        for material in self.component.materials.all():    
            oe = _get_operation_estimates(material, order_quantity, self.operation_estimates.all())
            operation_estimates.append(oe)

        service_estimate = Service.Estimate(order_quantity, operation_estimates)

        return service_estimate


class OperationEstimateManager(models.Manager):
    def create_operation_estimate(self, operation_template, service, material=None):
        name = operation_template.name
        operation_options = operation_template.operation_option_templates.all()

        operation_estimate = OperationEstimate.objects.create(
            name=name, service=service, material=material)

        for operation_option in operation_options:
            for step in operation_option.meta_operation_option.operation_steps:
                activity = step.activity
                ActivityEstimate.objects.create_activity_estimate(
                    activity, step.sequence, 
                    activity.set_up, activity.tear_down,
                    step.notes, operation_estimate)


class OperationEstimate(models.Model):
    class Estimate:
        def __init__(self, name, activity_estimates):
            self.name = name
            self.activity_estimates = activity_estimates
            
    objects = OperationEstimateManager()
    name = models.CharField(max_length=50, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, 
        related_name='operation_estimates')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='operation_estimates')


class ActivityEstimateManager(models.Manager):
    def create_activity_estimate(self, activity, sequence, set_up, tear_down, 
            notes, operation_estimate):
        name = activity.name
        measure_unit = activity.measure_unit
        activity_speed = activity.speed

        activity_estimate = ActivityEstimate.objects.create(
            operation_estimate=operation_estimate,
            name=name, sequence=sequence, 
            set_up=set_up, tear_down=tear_down,
            measure_unit=measure_unit, notes=notes)
        
        SpeedEstimate.objects.create(activity_estimate=activity_estimate,
            measure_value=activity_speed.measure_value, 
            measure_unit=activity_speed.measure_unit, 
            speed_unit=activity_speed.speed_unit)

        for activity_expense in activity.activity_expenses.all():
            ActivityExpenseEstimate.objects.create(
                activity_estimate=activity_estimate,
                name=activity_expense.name,
                type=activity_expense.type,
                rate=activity_expense.rate)


class ActivityEstimate(models.Model):
    class Estimate:
        def __init__(self, name, notes, activity_expense_estimates):
            self.name = name
            self.notes = notes
            self.activity_expense_estimates = activity_expense_estimates

    objects = ActivityEstimateManager()
    name = models.CharField(max_length=50, null=True)
    operation_estimate = models.ForeignKey(OperationEstimate, on_delete=models.CASCADE,
        related_name='activity_estimates')
    sequence = models.IntegerField(default=0)
    set_up = MeasurementField(measurement=Time, null=True, blank=False)
    tear_down = MeasurementField(measurement=Time, null=True, blank=False)
    measure_unit = models.CharField(max_length=20, blank=True, null=True)
    notes = models.CharField(max_length=20, blank=True, null=True)

    def get_duration(self, measurement, contingency=0, hours_per_day=10):
        self._validate_measurement(measurement)

        if self.speed_estimate is None:
            raise Exception('Activity speed is currently null and has not been initialized.')

        # factor hours for setup and teardown, multiplied by estimate num of days
        def __compute_overall(base_duration):
            overall = base_duration
            if self.set_up is not None and self.tear_down is not None:
                misc_hrs = (self.set_up.hr + self.tear_down.hr)
                run_hours = hours_per_day - misc_hrs
                estimate_days = math.ceil(base_duration / run_hours)
                overall = base_duration + (misc_hrs * estimate_days)
            return round(overall, 2)

        duration = 0
        measure_uom = Measure.STANDARD_UNITS[self.speed_estimate.measure]
        speed_uom = Measure.STANDARD_SPEED_UNITS[self.speed_estimate.measure]

        if measure_uom is not None and speed_uom is not None and \
                measurement is not None and self.speed_estimate is not None:
            mval = getattr(measurement, measure_uom)
            sval = getattr(self.speed_estimate.rate, speed_uom)

            if mval is not None and sval is not None:
                base = mval / sval
                multiplier = (contingency / 100) + 1
                duration = __compute_overall(base * multiplier)

        return Time(hr=duration)

    def _validate_measurement(self, measurement):
        try:
            if measurement is not None:
                uom = self.speed_estimate.measure_unit
                converted = getattr(measurement, uom)
                # if still successful at this point, then validation is done
                return
            else:
                raise Exception("Expected parameter 'measurement' is null")
        except AttributeError as e:
            uom = self.speed_estimate.measure_unit
            measure = Measure.get_measure(uom)
            raise MeasurementMismatch(measurement, measure)


class SpeedEstimate(Speed):
    activity_estimate = models.OneToOneField(ActivityEstimate, on_delete=models.CASCADE,
        related_name='speed_estimate')


class ActivityExpenseEstimate(models.Model):
    class Estimate:
        def __init__(self, name, uom, type, rate, rate_label, 
                measurement, duration):
            self.name = name
            self.uom = uom
            self.type = type
            self.rate = rate
            self.rate_label = rate_label
            self.measurement = measurement
            self.duration = duration
        
        @property
        def quantity(self):
            if self.type == ActivityExpense.HOUR_BASED:
                return self.duration.hr
            elif self.type == ActivityExpense.MEASURE_BASED:
                measurement = getattr(self.measurement, self.uom)
                return measurement
        
        @property
        def cost(self):
            total = self.rate
            if self.type in [ActivityExpense.HOUR_BASED, ActivityExpense.MEASURE_BASED]:
                total = self.rate * self.quantity
            return total
            
    name = models.CharField(max_length=50, null=True)
    activity_estimate = models.ForeignKey(ActivityEstimate, on_delete=models.CASCADE,
        related_name='activity_expense_estimates')
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