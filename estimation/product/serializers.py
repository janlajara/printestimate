from json import JSONEncoder
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from django.shortcuts import get_object_or_404
from djmoney.contrib.django_rest_framework import MoneyField
from core.utils.measures import MeasurementSerializerField
from inventory.models import Item
from estimation.template.models import ProductTemplate
from estimation.product.models import ProductEstimate, \
    EstimateQuantity, Product, Component, Service, \
    ActivityEstimate, OperationEstimate, Material
from estimation.costaddons.models import EstimateAddonItem, EstimateAddonSet
from estimation.machine.serializers import SheetLayoutMetaSerializer
from estimation.costaddons.serializers import AddonCostSetSerializer, \
    EstimateAddonItemSerializer, EstimateAddonSetSerializer


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['material_id', 'label']


class ComponentSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True)

    class Meta:
        model = Component
        fields = ['id', 'name', 'quantity', 'materials']


class ActivityEstimateSerializer(serializers.ModelSerializer):
    speed = serializers.SerializerMethodField()

    class Meta:
        model = ActivityEstimate
        fields = ['id', 'name', 'machine_name', 'sequence', 'speed', 'notes']

    def get_speed(self, instance):
        return instance.speed_estimate.rate_formatted


class OperationEstimateSerializer(serializers.ModelSerializer):
    material = serializers.SerializerMethodField()
    activity_estimates = ActivityEstimateSerializer(many=True)

    class Meta:
        model = OperationEstimate
        fields = ['id', 'name', 'material', 'activity_estimates']

    def get_material(self, instance):
        if instance.material is not None:
            return instance.material.item.name


class ServiceSerializer(serializers.ModelSerializer):
    operation_estimates = OperationEstimateSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'sequence', 'operation_estimates']


class ProductSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True)
    services = ServiceSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'components', 'services']


class MaterialEstimateSerializer(serializers.Serializer):
    order_quantity = serializers.IntegerField(min_value=1)
    estimated_stock_quantity = serializers.IntegerField(min_value=1)
    estimated_spoilage_quantity = serializers.IntegerField(min_value=1)
    estimated_total_quantity = serializers.IntegerField(min_value=1)


class MaterialSerializer(serializers.Serializer):
    name = serializers.CharField()
    rate = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')
    uom = serializers.CharField()
    spoilage_rate = serializers.DecimalField(default=0, max_digits=None, decimal_places=2)
    estimates = MaterialEstimateSerializer(many=True, read_only=True)
    layouts_meta = SheetLayoutMetaSerializer(many=True, read_only=True)


class ActivityExpenseEstimateEstimateSerializer(serializers.Serializer):
    uom = serializers.CharField()
    rate = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')
    order_quantity = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(default=0, max_digits=None,  decimal_places=2)
    cost = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')


class ActivityExpenseEstimateSerializer(serializers.Serializer):
    name = serializers.CharField()
    rate = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')
    type = serializers.CharField()
    rate_label = serializers.CharField()
    estimates = ActivityExpenseEstimateEstimateSerializer(many=True, read_only=True)


class ActivityEstimateSerializer(serializers.Serializer):
    name = serializers.CharField()
    notes = serializers.CharField()
    activity_expense_estimates = ActivityExpenseEstimateSerializer(many=True, read_only=True)


class OperationEstimateSerializer(serializers.Serializer):
    name = serializers.CharField()
    item_name = serializers.CharField()
    activity_estimates = ActivityEstimateSerializer(many=True, read_only=True)


class ServiceEstimateSerializer(serializers.Serializer):
    name = serializers.CharField()
    duration_estimates_map = serializers.DictField(
        child=MeasurementSerializerField(decimal_places=2))
    operation_estimates = OperationEstimateSerializer(many=True, read_only=True)


class ProductEstimateInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    product_template_id = serializers.IntegerField()
    order_quantities = serializers.ListField(child=serializers.IntegerField(min_value=1))


class ProductEstimateSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    order_quantities = serializers.ListField(child=serializers.IntegerField(min_value=1))
    estimate_addon_set = EstimateAddonSetSerializer()

    class Meta:
        model = ProductEstimate
        fields = ['id', 'name', 'description', 'estimate_code', 'template_code', 
            'order_quantities', 'material_spoilage_rate', 'product', 'estimate_addon_set']


class ProductEstimateListSerializer(serializers.ModelSerializer):
    order_quantities = serializers.ListField(child=serializers.IntegerField(min_value=1))

    class Meta:
        model = ProductEstimate
        fields = ['id', 'name', 'description', 'template_code', 'order_quantities']


class ProductEstimateInputSerializer(ProductEstimateListSerializer):
    id = serializers.IntegerField(required=False)
    estimate_addon_set = EstimateAddonSetSerializer()

    class Meta:
        model = ProductEstimate
        fields = ['id', 'product_template', 'order_quantities', 
            'material_spoilage_rate', 'estimate_addon_set']

    def create(self, validated_data):
        product_template = validated_data.get('product_template')
        order_quantities = validated_data.get('order_quantities')
        material_spoilage_rate = validated_data.get('material_spoilage_rate')

        product_estimate = ProductEstimate.objects.create_product_estimate(
                product_template, order_quantities, material_spoilage_rate)

        estimate_addon_set_data = validated_data.get('estimate_addon_set')
        if estimate_addon_set_data is not None:
            cost_addons_data = estimate_addon_set_data.get('estimate_addon_items', [])
            if len(cost_addons_data) > 0:
                addon_set = EstimateAddonSet.objects.create(product_estimate=product_estimate)

                for index, addon_data in enumerate(cost_addons_data):
                    name = addon_data.get('name')
                    sequence = index+1
                    type = addon_data.get('type')
                    value = addon_data.get('value')
                    allow_custom_value = addon_data.get('allow_custom_value')
                    config_cost_addon = addon_data.get('config_cost_addon')

                    addon_set.add_addon_item(name=name, sequence=sequence,
                        type=type, value=value, allow_custom_value=allow_custom_value,
                        config_cost_addon=config_cost_addon)

        return product_estimate

    def update(self, instance, validated_data):
        def _delete_addons(as_is_addons, to_be_addons):
            as_is_pks = [x.id for x in as_is_addons]
            to_be_pks = [x.get('id') for x in to_be_addons if 'id' in x]
            to_delete = [x for x in as_is_pks if x not in to_be_pks]
            EstimateAddonItem.objects.filter(pk__in=to_delete).delete()

        def _update_items(to_be_addons):
            for index, addon_data in enumerate(to_be_addons):
                existing_id = addon_data.get('id')
                if existing_id is not None:
                    addon = get_object_or_404(EstimateAddonItem, pk=existing_id)
                    addon.name = addon_data.get('name', addon.name)
                    addon.sequence = addon_data.get('sequence', addon.sequence)
                    addon.type = addon_data.get('type', addon.type)
                    addon.value = addon_data.get('value', addon.value)
                    addon.allow_custom_value = addon_data.get('allow_custom_value', addon.allow_custom_value)
                    addon.save()
                else:
                    name = addon_data.get('name')
                    sequence = index+1
                    type = addon_data.get('type')
                    value = addon_data.get('value')
                    allow_custom_value = addon_data.get('allow_custom_value')
                    config_cost_addon = addon_data.get('config_cost_addon')
                    instance.estimate_addon_set.add_addon_item(name=name, sequence=sequence,
                        type=type, value=value, allow_custom_value=allow_custom_value,
                        config_cost_addon=config_cost_addon)

        order_quantities = validated_data.get('order_quantities')
        material_spoilage_rate = validated_data.get('material_spoilage_rate')
        instance.set_estimate_quantities(order_quantities)
        instance.set_material_spoilage_rate(material_spoilage_rate)
        
        estimate_addon_set_data = validated_data.get('estimate_addon_set')
        if estimate_addon_set_data is not None:
            cost_addons_data = estimate_addon_set_data.get('estimate_addon_items', [])
            if len(cost_addons_data) > 0:
                addon_set = None
                if not hasattr(instance, 'estimate_addon_set'):
                    addon_set = EstimateAddonSet.objects.create(product_estimate=instance)
                else:
                    addon_set = instance.estimate_addon_set
                    _delete_addons(addon_set.estimate_addon_items.all(), cost_addons_data)

                _update_items(cost_addons_data)
            
        return instance


class ProductEstimateEstimatesSerializer(serializers.Serializer):
    material_estimates = MaterialSerializer(many=True, required=False, read_only=True)
    service_estimates = ServiceEstimateSerializer(many=True, required=False, read_only=True)


class ProductEstimateSummaryPriceSerializer(serializers.Serializer):
    order_quantity = serializers.IntegerField()
    price = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')
    total_addons = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')
    total_price = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')


class ProductEstimateSummaryDurationSerializer(serializers.Serializer):
    order_quantity = serializers.IntegerField()
    duration = MeasurementSerializerField(decimal_places=2)


class ProductEstimateSummarySerializer(serializers.Serializer):
    order_quantities = serializers.ListField(child=serializers.IntegerField(min_value=1))
    prices = ProductEstimateSummaryPriceSerializer(many=True)
    durations = ProductEstimateSummaryDurationSerializer(many=True)


class ProductEstimateCostsSerializer(ProductEstimateSerializer):
    summary = ProductEstimateSummarySerializer(read_only=True)
    estimates = ProductEstimateEstimatesSerializer(read_only=True)
    cost_addons = AddonCostSetSerializer(read_only=True, many=True)

    class Meta:
        model = ProductEstimate
        fields = ['id', 'name', 'description', 'template_code', 
            'summary', 'estimates', 'cost_addons']