import math, decimal
from measurement.utils import guess
from cached_property import cached_property
from decimal import Decimal
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_measurement.models import MeasurementField
from core.utils.measures import Quantity, CostingMeasure, Measure
from measurement.measures import Time
from inventory.models import Item
from inventory.properties.models import Shape, Tape, Line, Paper, Panel, Liquid
from estimation.metaproduct.models import MetaEstimateVariable, MetaService
from estimation.process.models import ActivityExpense, Speed
from estimation.template.models import ProductTemplate, ComponentTemplate, OperationOptionTemplate
from estimation.machine.models import Machine, ChildSheet, RollFedPressMachine
from estimation.exceptions import MaterialTypeMismatch, MeasurementMismatch
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from djmoney.models.fields import MoneyField

class ProductEstimateManager(models.Manager):

    def create_product_estimate(self, product_template, quantities=None, material_spoilage_rate=0):
        product_estimate = ProductEstimate.objects.create(product_template=product_template,
            material_spoilage_rate=material_spoilage_rate)

        if quantities is not None:
            for quantity in quantities:
                EstimateQuantity.objects.create(product_estimate=product_estimate, quantity=quantity)

        product = Product.objects.create_product(product_template, product_estimate)

        return product_estimate


class ProductEstimate(models.Model):
    class Summary:
        def __init__(self, order_quantities, prices, durations):
            self.order_quantities = order_quantities
            self.prices = prices
            self.durations = durations

        class Price:
            def __init__(self, order_quantity, price, addons=[]):
                self.order_quantity = order_quantity
                self.price = price
                self.addons = addons

            @property
            def price_value(self):
                return self.price.amount
            
            @property
            def total_addons(self):
                total_addons = 0
                for addon in self.addons:
                    total_addons += addon.addon_cost
                return total_addons

            @property
            def total_price(self):
                return self.price_value + self.total_addons

        class Duration:
            def __init__(self, order_quantity, duration):
                self.order_quantity = order_quantity
                self.duration = duration
            
            @property
            def duration_value(self):
                return self.duration.hr

    class Estimate:
        def __init__(self, id, product_template_id, order_quantities, 
                material_estimates, service_estimates):
            self.id = id
            self.product_template_id = product_template_id
            self.order_quantities = order_quantities
            self.material_estimates = material_estimates
            self.service_estimates = service_estimates
    
        @property
        def total_prices_map(self):
            def _initialize_totals(container, estimates):
                for estimate in estimates:
                    for (key, value) in estimate.total_prices_map.items():
                        container[key] = container.get(key, 0) + value
            totals = {}
            _initialize_totals(totals, self.material_estimates + self.service_estimates)
            return totals

        @property
        def duration_estimates_map(self):
            durations = {}
            for estimate in self.service_estimates:
                for (key, value) in estimate.duration_estimates_map.items():
                    durations[key] = durations.get(key, Time(hr=0)) + value
            return durations
            
    objects = ProductEstimateManager()
    product_template = models.ForeignKey(ProductTemplate, null=True, 
        on_delete=models.SET_NULL, related_name='product_estimates')
    material_spoilage_rate = models.DecimalField(max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    @property
    def estimate_code(self):
        return 'CE-%s' %  (str(self.id).zfill(4))

    @property
    def name(self):
        if self.product is not None:
            return self.product.name
    
    @property
    def description(self):
        if self.product is not None:
            return self.product.description

    @property
    def template_code(self):
        if self.product is not None:
            return self.product_template.code

    @property
    def order_quantities(self):
        quantities = [estimate_quantity.quantity 
            for estimate_quantity 
            in self.estimate_quantities.order_by('quantity').all()]
        return quantities

    @property
    def summary(self):
        prices_map = self.estimates.total_prices_map
        durations_map = self.estimates.duration_estimates_map
        prices = []
        durations = []
        
        for (key, value) in prices_map.items():
            cost_addon_set = next((x for x in self.cost_addons 
                if x.order_quantity ==  key), None)
            addon_costs = cost_addon_set.addon_costs if cost_addon_set is not None else []
            price = ProductEstimate.Summary.Price(key, value, addon_costs)
            prices.append(price)

        for (key, value) in durations_map.items():
            duration = ProductEstimate.Summary.Duration(key, value)
            durations.append(duration)

        return ProductEstimate.Summary(self.order_quantities, prices, durations)

    @cached_property
    def estimates(self):

        def _get_material_estimates(components):
            material_estimates = []
            for component in components:
                for material in component.materials.all():
                    me = material.estimates
                    material_estimates.append(me)
                    
            return material_estimates

        def _get_service_estimates(services):
            service_estimates = []
            for service in services:
                se = service.estimates
                service_estimates.append(se)
            return service_estimates
            
        product_estimates = []
        order_quantities = [estimate_quantity.quantity 
            for estimate_quantity in self.estimate_quantities.all()]

        product = self.product
        product_template_id = (self.product_template.pk 
            if self.product_template is not None else None)
            
        material_estimates = _get_material_estimates(product.components.all())
        service_estimates = _get_service_estimates(product.services.all())

        product_estimate = ProductEstimate.Estimate(
            self.pk, product_template_id, order_quantities,
            material_estimates, service_estimates)

        return product_estimate
    
    @property
    def cost_addons(self):
        cost_addons = []
        if hasattr(self, 'estimate_addon_set'):
            prices_map = self.estimates.total_prices_map
            for (quantity, price) in prices_map.items():
                cost_addon_set = self.estimate_addon_set.get_addon_cost_set(quantity, price.amount)
                cost_addons.append(cost_addon_set)
        return cost_addons

    def set_material_spoilage_rate(self, spoilage_rate):
        self.material_spoilage_rate = spoilage_rate
        self.save()
        
        for component in self.product.components.all():
            for material in component.materials.all():
                material.spoilage_rate = spoilage_rate
                material.save()

    def set_estimate_quantities(self, order_quantities):
        if order_quantities is not None and not isinstance(order_quantities, list):
            raise Exception("Provided argument 'order_quantities' must be a list of integers")

        order_quantities.sort()

        if order_quantities != self.order_quantities:
            to_delete = EstimateQuantity.objects.filter(
                product_estimate=self).exclude(
                    quantity__in=order_quantities)
            to_delete.delete()

            for order_quantity in order_quantities:
                if order_quantity not in self.order_quantities:
                    EstimateQuantity.objects.create(product_estimate=self, 
                        quantity=order_quantity)


class EstimateQuantity(models.Model):
    product_estimate = models.ForeignKey(ProductEstimate, on_delete=models.CASCADE,
        related_name='estimate_quantities')
    quantity = models.IntegerField(default=1)


class ProductManager(models.Manager):
    def create_product(self, product_template, product_estimate=None):
        product = Product.objects.create(name=product_template.name, 
            description=product_template.description,
            product_estimate=product_estimate)
        components_map = {}

        for component_template in product_template.component_templates.all():
            component = Component.objects.create_component_by_template(component_template, product)
            components_map[component_template.pk] = component
    
        for service_template in product_template.service_templates.order_by('meta_service__sequence'):
            component = None
            if service_template.component_template is not None:
                component = components_map.get(service_template.component_template.pk, None)

            has_operation_option_template = len(OperationOptionTemplate.objects.filter(
                operation_template__service_template=service_template).all()) > 0
            if has_operation_option_template:
                service = Service.objects.create_service(service_template, product, component)


class Product(models.Model):
    objects = ProductManager()
    name = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=100, null=True)
    product_estimate = models.OneToOneField(ProductEstimate, on_delete=models.CASCADE,
        null=True, blank=True, related_name='product')


class ComponentManager(PolymorphicManager):

    @classmethod
    def get_class(cls, type):
        mapping = {
            Item.TAPE: TapeComponent,
            Item.LINE: LineComponent,
            Item.PAPER: PaperComponent,
            Item.PANEL: PanelComponent,
            Item.LIQUID: LiquidComponent,
            Item.OTHER: Component
        }
        clazz = mapping.get(type, Component)
        return clazz

    def create_component(self, name, type, product, quantity, **kwargs):
        clazz = ComponentManager.get_class(type)
        return clazz.objects.create(name=name, product=product, 
            quantity=quantity, **kwargs)


    def create_component_by_template(self, component_template, product):
        name = component_template.name
        machine = component_template.machine_option.machine if \
            component_template.machine_option is not None and \
            component_template.machine_option.machine is not None else None
        clazz = ComponentManager.get_class(component_template.type)
        component = clazz.objects.create(name=name, 
            machine=machine, product=product,
            quantity=component_template.quantity,
            **component_template.prop_args)
        material_spoilage_rate = product.product_estimate.material_spoilage_rate

        for material_template in component_template.material_templates.all():
            material = Material.objects.create_material(component, 
                material_template.type, material_template.item,
                material_template.item.price, material_spoilage_rate)
        
        return component


class Component(PolymorphicModel, Shape):
    objects = ComponentManager()
    name = models.CharField(max_length=40, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
        related_name='components')
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL,
        null=True)
    quantity = models.IntegerField(default=1)

    def get_costing_measurements_map(self, order_quantity):
        set_material_measures = {
            CostingMeasure.QUANTITY: Quantity(pc=order_quantity)}
        total_material_measures = {
            CostingMeasure.QUANTITY: Quantity(pc=order_quantity * self.quantity)}

        return {
            MetaEstimateVariable.SET_MATERIAL: set_material_measures,
            MetaEstimateVariable.TOTAL_MATERIAL: total_material_measures
        }


class TapeComponent(Component, Tape):
    pass


class LineComponent(Component, Line):
    pass


class PaperComponent(Component, Paper):

    def get_costing_measurements_map(self, order_quantity):
        layout = self.layout 

        set_material_measures = {
            CostingMeasure.QUANTITY: Quantity(pc=order_quantity),
            CostingMeasure.AREA: layout.area_measurement * order_quantity,
            CostingMeasure.PERIMETER: layout.perimeter_measurement * order_quantity}

        total_quantity = order_quantity * self.quantity
        total_material_measures = {
            CostingMeasure.QUANTITY: Quantity(pc=total_quantity),
            CostingMeasure.AREA: layout.area_measurement * total_quantity,
            CostingMeasure.PERIMETER: layout.perimeter_measurement * total_quantity}

        measurements_map = {
            MetaEstimateVariable.SET_MATERIAL: set_material_measures,
            MetaEstimateVariable.TOTAL_MATERIAL: total_material_measures
        }
        
        return measurements_map


class PanelComponent(Component, Panel):
    pass


class LiquidComponent(Component, Liquid):
    pass


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

    def create_material(self, component, type, item, price=0, spoilage_rate=0):
        if item.type != type:
            raise MaterialTypeMismatch(item.type, type)
        if price is None:
            price = 0

        clazz = MaterialManager.get_class(type)
        material = clazz.objects.create(component=component, 
            item=item, price=price, spoilage_rate=spoilage_rate)
        return material


class Material(PolymorphicModel):

    class Material:
        def __init__(self, name, rate, uom, spoilage_rate, estimates=[], machine_type=None):
            self.name = name
            self.rate = rate
            self.uom = uom
            self.spoilage_rate = spoilage_rate
            self.estimates = estimates
            self.machine_type = machine_type
            self.layouts_meta = []

        @cached_property
        def total_prices_map(self):
            return {estimate.order_quantity: 
                estimate.estimated_total_quantity * self.rate 
                for estimate in self.estimates}

        @cached_property
        def estimates_map(self):
            return {estimate.order_quantity: estimate for estimate in self.estimates}

    class Estimate:
        def __init__(self, order_quantity, material_quantity, 
                spoilage_rate=0, layouts_meta=None, layout_type=None):
            self.order_quantity = order_quantity
            self.material_quantity = material_quantity
            self.spoilage_rate = spoilage_rate
            self.layouts_meta = layouts_meta
            self.layout_type = layout_type
        
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
            value = self.order_quantity
            return {CostingMeasure.QUANTITY: Quantity(pc=value)}

        @property
        def total_material_quantity(self):
            return self.order_quantity * self.material_quantity

        @property
        def total_material_measures(self):
            total_material = self.total_material_quantity
            return {CostingMeasure.QUANTITY: Quantity(pc=total_material)}

        @property
        def machine_run_measures(self):
            pass

        @cached_property
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
    spoilage_rate = models.DecimalField(max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)

    @classmethod
    def get_class(cls, type):
        return cls.objects.get_class(type)

    @property
    def label(self):
        return '%s %s' % (self.item.name, self.component)

    @property
    def quantity(self):
        quantity = 1
        if self.component is not None:
            quantity = self.component.quantity
        return quantity

    @property
    def item_properties(self):
        return self.item.properties

    @property
    def estimates(self):
        product_estimate = self.component.product.product_estimate
        quantities = [
            estimate_quantity.quantity
            for estimate_quantity 
            in product_estimate.estimate_quantities.all()]
        material_estimate = self.estimate(quantities, self.spoilage_rate)
        return material_estimate

    def estimate(self, order_quantities, spoilage_rate=0):
        if not isinstance(order_quantities, list):
            raise Exception("Provided argument to method 'estimate' must be a list of integers.")

        material_estimate = Material.Material(
            self.item.name, self.price, 
            self.item.base_uom, spoilage_rate)

        estimates = []
        for quantity in order_quantities:
            estimate = Material.Estimate(quantity, self.component.quantity,
                spoilage_rate)
            estimates.append(estimate)
        material_estimate.estimates = estimates
        
        return material_estimate
        

class TapeMaterial(Material):
    pass


class LineMaterial(Material):
    pass


class PaperMaterial(Material):
    class Estimate(Material.Estimate):

        @property
        def layouts(self):
            layouts = {
                'parent_sheet': None,
                'run_sheet': None,
                'final_sheet': None
            }

            if self.layouts_meta is not None:

                if self.layout_type == Machine.SHEET_FED_PRESS or \
                        self.layout_type == Machine.ROLL_FED_PRESS:
                    parent_to_runsheet = self.layouts_meta[0]
                    runsheet_to_finalsheet = self.layouts_meta[1]
                    layouts = {
                        'parent_sheet': parent_to_runsheet.bin,
                        'run_sheet': parent_to_runsheet.rect,
                        'final_sheet': runsheet_to_finalsheet.rect}
                else:
                    parent_to_finalsheet = self.layouts_meta[0]
                    layouts = {
                        'parent_sheet': parent_to_finalsheet.bin,
                        'run_sheet': parent_to_finalsheet.rect,
                        'final_sheet': parent_to_finalsheet.rect}

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
                raw_to_runsheet_layout_meta = self.layouts_meta[0]
                runsheet_per_raw_material = raw_to_runsheet_layout_meta.count
                machine_run_quantity = math.ceil(self.estimated_total_quantity * 
                    runsheet_per_raw_material)
        
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

            if self.layouts_meta is not None and \
                    self.layout_type == Machine.SHEET_FED_PRESS:
                item_to_parent_layout_meta = self.layouts_meta[0]
                cut_count = item_to_parent_layout_meta.cut_count

            return cut_count
        
        @property
        def running_to_final_cut(self):
            cut_count = 0
            
            if self.layouts_meta is not None and \
                    self.layout_type == Machine.SHEET_FED_PRESS:
                parent_to_child_layout_meta = self.layouts_meta[1]
                cut_count = parent_to_child_layout_meta.cut_count
            
            return cut_count
        
        @property
        def raw_to_final_cut(self):
            cut_count = 0

            if self.layouts_meta is not None and \
                    self.layout_type != Machine.SHEET_FED_PRESS:
                item_to_child_layout_meta = self.layouts_meta[0]
                cut_count = item_to_child_layout_meta.cut_count

            return cut_count

        @cached_property
        def output_per_item(self):
            output_per_item = 0

            if self.layouts_meta is not None:
                if self.layout_type == Machine.SHEET_FED_PRESS:
                    raw_to_running_layout_meta = self.layouts_meta[0]
                    running_to_final_layout_meta = self.layouts_meta[1]

                    running_per_raw = raw_to_running_layout_meta.count
                    final_per_running = running_to_final_layout_meta.count
                    output_per_item = running_per_raw * final_per_running

                else: 
                    item_to_child_layout_meta = self.layouts_meta[0]
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

    class RollFedMachineEstimate(Estimate):
        def __init__(self, order_quantity, material_quantity, 
                spoilage_rate=0, layouts_meta=None, layout_type=None):
            super().__init__(order_quantity, material_quantity, 
                spoilage_rate=spoilage_rate, layouts_meta=layouts_meta, 
                layout_type=layout_type)

        @property
        def raw_to_running_cut(self):
            cut_count = 0
            if self.layouts_meta is not None:
                raw_to_running_meta = self.layouts_meta[0]
                cut_count = max(raw_to_running_meta.cut_count, 4)
            return cut_count
        
        @property
        def running_to_final_cut(self):
            cut_count = 0
            if self.layouts_meta is not None:
                running_to_final_meta = self.layouts_meta[1]
                cut_count = running_to_final_meta.cut_count
            return cut_count
        
        @property
        def raw_to_final_cut(self):
            cut_count = self.raw_to_running_cut + self.running_to_final_cut
            return cut_count

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
        def machine_run_measures(self):
            total_quantity = float(self.estimated_total_quantity)
            parent_sheet = self.layouts.get('parent_sheet') 
            measures = {
                CostingMeasure.QUANTITY: Quantity(roll=total_quantity),
                CostingMeasure.AREA: parent_sheet.area_measurement * total_quantity}

            raw_to_running_layout_meta = self.layouts_meta[0]
            running_to_final_layout_meta = self.layouts_meta[1]
            running_per_raw = raw_to_running_layout_meta.count
            final_per_running = running_to_final_layout_meta.count
            final_sheets_count = (running_per_raw * final_per_running)
            final_sheet = self.layouts.get('final_sheet') 
            perimeter = {CostingMeasure.PERIMETER: 
                final_sheet.perimeter_measurement * final_sheets_count}

            measures.update(perimeter)

            return measures

        @property
        def estimated_stock_quantity(self):
            spoilage_divisor = (self.spoilage_rate / 100) + 1
            total_outs = decimal.Decimal(self.output_per_item)
            return total_outs / spoilage_divisor 

        @property
        def estimated_spoilage_quantity(self):
            spoilage_multiplier = (self.spoilage_rate / 100)
            total_outs = decimal.Decimal(self.output_per_item)
            return total_outs * spoilage_multiplier

        @property
        def estimated_total_quantity(self):
            return self.estimated_stock_quantity + self.estimated_spoilage_quantity

        @cached_property
        def output_per_item(self):
            output_per_item = 0

            if self.layouts_meta is not None and self.layout_type == Machine.ROLL_FED_PRESS:
                raw_to_running_layout_meta = self.layouts_meta[0]
                running_to_final_layout_meta = self.layouts_meta[1]

                running_per_raw = raw_to_running_layout_meta.count
                final_per_running = running_to_final_layout_meta.count

                raw_length = raw_to_running_layout_meta.bin.length
                running_length = raw_to_running_layout_meta.rect.length
                final_sheets_count = (running_per_raw * final_per_running)

                if running_per_raw > 0 and (raw_length > running_length or \
                        self.total_material_quantity > final_sheets_count):
                    multiplier = self.total_material_quantity / max(final_sheets_count, 1)
                    total_running_length = running_per_raw * multiplier * running_length
                    output_per_item = total_running_length / raw_length
                else:
                    output_per_item = running_length / raw_length
            
            return output_per_item

    def _get_rollfed_layout_estimates(self, order_quantities, raw_material_layout, 
            final_material_layout, rotate, spoilage_rate):
        layouts = []
        estimates = []
        machine = self.component.machine
        machine_layout_type = None

        for quantity in order_quantities:
            set_quantity = self.component.quantity
            total_quantity = quantity * set_quantity
            layouts, machine_layout_type = machine.get_sheet_layouts(raw_material_layout, 
                final_material_layout, rotate, order_quantity=total_quantity, 
                spoilage_rate=spoilage_rate)

            estimate = PaperMaterial.RollFedMachineEstimate(quantity, 
                self.component.quantity, spoilage_rate, layouts, machine_layout_type)
            estimates.append(estimate)
        
        return layouts, estimates

    def _get_default_layout_estimates(self, order_quantities, raw_material_layout, 
            final_material_layout, rotate, spoilage_rate):
        layouts = []
        machine_layout_type = None
        
        machine = self.component.machine
        if machine is not None:
            layouts, machine_layout_type = machine.get_sheet_layouts(
                raw_material_layout, final_material_layout, rotate)
        else:
            layouts = [ChildSheet.get_layout(raw_material_layout, 
                final_material_layout, rotate)]
        
        estimates = []
        for quantity in order_quantities:
            estimate = PaperMaterial.Estimate(quantity, self.component.quantity,
                spoilage_rate, layouts, machine_layout_type)
            estimates.append(estimate)
        
        return layouts, estimates

    def estimate(self, order_quantities, spoilage_rate=0, rotate=True):
        machine_type = (self.component.machine.type 
            if self.component.machine is not None else None)
        raw_material_name = self.item.full_name
        paper_estimate = Material.Material(raw_material_name, self.price, 
            self.item.base_uom, spoilage_rate, machine_type=machine_type)

        if self.item is not None:
            layouts = []
            estimates = []

            if self.component is not None:
                if machine_type == Machine.ROLL_FED_PRESS:
                    layouts, estimates = self._get_rollfed_layout_estimates(
                        order_quantities, self.item_properties.layout, 
                        self.component.layout, rotate, spoilage_rate)
                else:
                    layouts, estimates = self._get_default_layout_estimates(
                        order_quantities, self.item_properties.layout, 
                        self.component.layout, rotate, spoilage_rate)

            paper_estimate.layouts_meta = layouts
            paper_estimate.estimates = estimates
        
        return paper_estimate
 
 
class PanelMaterial(Material):
    pass


class LiquidMaterial(Material):
    pass


class ServiceManager(models.Manager):
    def create_service(self, service_template, product, component=None):
        def _create_operation_estimate(operation_template, service, component_material=None):
            OperationEstimate.objects.create_operation_estimate(
                    operation_template, service, component_material)

        name = service_template.name
        sequence = service_template.sequence
        costing_measure = service_template.costing_measure
        estimate_variable_type = service_template.estimate_variable_type
        input_quantity = service_template.input_quantity

        service = Service.objects.create(name=name, product=product, 
            sequence=sequence, component=component, costing_measure=costing_measure,
            estimate_variable_type=estimate_variable_type, input_quantity=input_quantity)
        component_materials = component.materials.all() if component is not None else []

        for operation_template in service_template.operation_templates.all():
            if service_template.measure_basis == MetaService.MeasureBasis.MATERIAL and \
                    len(component_materials) > 0:
                for component_material in component_materials:
                    _create_operation_estimate(operation_template, service, component_material)
            else:
                _create_operation_estimate(operation_template, service)

        return service
        

class Service(models.Model):
    class Estimate:
        def __init__(self, name, operation_estimates):
            self.name = name
            self.operation_estimates = operation_estimates
        
        @property
        def total_prices_map(self):
            totals = {}
            for estimate in self.operation_estimates:
                for (key, value) in estimate.total_prices_map.items():
                    totals[key] = totals.get(key, 0) + value
            return totals 
        
        @property
        def duration_estimates_map(self):
            durations = {}
            for estimate in self.operation_estimates:
                for (key, value) in estimate.duration_estimates_map.items():
                    durations[key] = durations.get(key, Time(hr=0)) + value
            return durations

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
    input_quantity = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    input_uom = models.CharField(max_length=20, choices=Measure.PRIMARY_UNITS,
        default='pc')

    @property
    def input_measure(self):
        if self.component is None:
            if self.costing_measure == CostingMeasure.QUANTITY:
                return Quantity(**{self.input_uom: self.input_quantity})
            else:
                return guess(self.input_quantity, self.input_uom)   

    @property
    def estimates(self):
        product_estimate = self.product.product_estimate
        quantities = [
            estimate_quantity.quantity
            for estimate_quantity 
            in product_estimate.estimate_quantities.all()]
        service_estimate = self.estimate(quantities)
        return service_estimate

    def estimate(self, order_quantities):
        if not isinstance(order_quantities, list):
            raise Exception("Provided argument to method 'estimate' must be a list of integers.")

        def _get_activity_expense_estimates(activity_expense_estimates):
            results = []
            for activity_expense_estimate in activity_expense_estimates:
                aee = ActivityExpenseEstimate.Expense.create(
                    activity_expense_estimate, order_quantities)
                results.append(aee)
            return results

        def _get_activity_estimates(activity_estimates):
            results = []
            for activity_estimate in activity_estimates:
                activity_expense_estimates = _get_activity_expense_estimates(
                    activity_estimate.activity_expense_estimates.all())
                ae = ActivityEstimate.Estimate(activity_estimate.name,
                    activity_estimate.notes, activity_expense_estimates)
                results.append(ae)
            return results

        def _get_operation_estimates(operation_estimates):
            results = []

            for operation_estimate in operation_estimates:
                activity_estimates = _get_activity_estimates(
                    operation_estimate.activity_estimates.all())
                item_name = operation_estimate.material.item.name if \
                    operation_estimate.material is not None and \
                    operation_estimate.material.item is not None else None
                oe = OperationEstimate.Estimate(
                    operation_estimate.name, item_name,
                    activity_estimates)
                results.append(oe)
            return results

        operation_estimates = _get_operation_estimates(self.operation_estimates.all())
        service_estimate = Service.Estimate(self.name, operation_estimates)

        return service_estimate


class OperationEstimateManager(models.Manager):
    def create_operation_estimate(self, operation_template, service, material=None):
        name = operation_template.name
        operation_options = operation_template.operation_option_templates.all()

        operation_estimate = OperationEstimate.objects.create(
            name=name, service=service, material=material)

        for operation_option in operation_options:
            machine = operation_option.meta_operation_option.machine_name
            operation_option_label = operation_option.label

            for step in operation_option.meta_operation_option.operation_steps:
                activity = step.activity
                ActivityEstimate.objects.create_activity_estimate(
                    activity, step.sequence, 
                    activity.set_up, activity.tear_down,
                    step.notes, operation_estimate, machine=machine,
                    operation_option_label=operation_option_label)


class OperationEstimate(models.Model):
    class Estimate:
        def __init__(self, name, item_name, activity_estimates):
            self.name = name
            self.item_name = item_name
            self.activity_estimates = activity_estimates

        @property
        def total_prices_map(self):
            totals = {}
            for estimate in self.activity_estimates:
                for (key, value) in estimate.total_prices_map.items():
                    totals[key] = totals.get(key, 0) + value
            return totals

        @property
        def duration_estimates_map(self):
            durations = {}
            for estimate in self.activity_estimates:
                for (key, value) in estimate.duration_estimates_map.items():
                    durations[key] = durations.get(key, Time(hr=0)) + value
            return durations
            
    objects = OperationEstimateManager()
    name = models.CharField(max_length=50, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, 
        related_name='operation_estimates')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='operation_estimates')
    measures_mapping_cache = {}

    def get_costing_measurement(self, order_quantity):
        estimate_variable_type = self.service.estimate_variable_type
        is_material_based = self.material is not None
        is_component_based = not is_material_based and self.service.component is not None
        is_input_quantity_based = not is_material_based and not is_component_based

        if is_input_quantity_based:
            return self.service.input_measure

        elif estimate_variable_type is not None and \
                self.service.costing_measure is not None:

            prefix = 'o'
            
            if is_material_based:
                prefix = 'm%s' % (self.material.pk)
            elif is_component_based:
                prefix = 'c%s' % (self.service.component.pk)

            key = '%s-%s' % (prefix, order_quantity)
            measures_mapping = self.measures_mapping_cache.get(key)
            
            if measures_mapping is None:
                if is_material_based:
                    material_estimate = self.material.estimates.estimates_map.get(
                        order_quantity)
                    measures_mapping = material_estimate.costing_measurements_map
                elif is_component_based:
                    measures_mapping = self.service.component.get_costing_measurements_map(order_quantity)

                self.measures_mapping_cache[key] = measures_mapping
            
            measures = measures_mapping.get(estimate_variable_type)

            if measures is not None:
                result = measures.get(self.service.costing_measure, None)
                return result



class ActivityEstimateManager(models.Manager):
    def create_activity_estimate(self, activity, sequence, set_up, tear_down, 
            notes, operation_estimate, machine=None, operation_option_label=None):
        name = operation_option_label
        measure_unit = activity.measure_unit
        activity_speed = activity.speed

        activity_estimate = ActivityEstimate.objects.create(
            machine_name=machine,
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
        def __init__(self, name, notes, activity_expense_estimates, 
                duration_estimates=[]):
            self.name = name
            self.notes = notes
            self.activity_expense_estimates = activity_expense_estimates
        
        @property
        def total_prices_map(self):
            totals = {}
            for estimate in self.activity_expense_estimates:
                for (key, value) in estimate.total_prices_map.items():
                    totals[key] = totals.get(key, 0) + value
            return totals

        @property
        def duration_estimates_map(self):
            durations = {}
            if len(self.activity_expense_estimates) > 0:
                expense = self.activity_expense_estimates[0]
                for estimate in expense.estimates:
                    durations[estimate.order_quantity] = estimate.duration
            return durations

    objects = ActivityEstimateManager()
    name = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=50, null=True)
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
        except Exception as e:
            raise e


class SpeedEstimate(Speed):
    activity_estimate = models.OneToOneField(ActivityEstimate, on_delete=models.CASCADE,
        related_name='speed_estimate')


class ActivityExpenseEstimate(models.Model):
    class Expense:
        def __init__(self, name, rate, type, rate_label, estimates=[]):
            self.name = name
            self.type = type
            self.rate = rate
            self.rate_label = rate_label
            self.estimates = estimates

        @property
        def total_prices_map(self):
            return {estimate.order_quantity: estimate.cost 
                for estimate in self.estimates}

        @classmethod
        def create(cls, activity_expense_estimate, order_quantities):
            expense_estimates = []
            for quantity in order_quantities:
                estimate = activity_expense_estimate.estimate(quantity)
                expense_estimates.append(estimate)
            aee = ActivityExpenseEstimate.Expense(
                activity_expense_estimate.name,
                activity_expense_estimate.rate,
                activity_expense_estimate.type,
                activity_expense_estimate.rate_label,
                expense_estimates)
            return aee

    class Estimate:
        def __init__(self, uom, type, rate, order_quantity, 
                measurement, duration):
            self.uom = uom
            self.type = type
            self.rate = rate
            self.order_quantity = order_quantity
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
                total = self.rate * Decimal(self.quantity)
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

    def estimate(self, order_quantity):
        activity_estimate = self.activity_estimate
        operation = activity_estimate.operation_estimate
        costing_measurement = operation.get_costing_measurement(order_quantity)
        estimate = None
        
        if costing_measurement is not None:
            duration = activity_estimate.get_duration(costing_measurement)
            estimate = ActivityExpenseEstimate.Estimate(
                self.uom, self.type, self.rate, 
                order_quantity, costing_measurement, duration)
        
        return estimate