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
from estimation.machine.serializers import SheetLayoutMetaSerializer


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

    class Meta:
        model = ProductEstimate
        fields = ['id', 'name', 'description', 'estimate_code', 'template_code', 
            'order_quantities', 'material_spoilage_rate', 'product']


class ProductEstimateListSerializer(serializers.ModelSerializer):
    order_quantities = serializers.ListField(child=serializers.IntegerField(min_value=1))

    class Meta:
        model = ProductEstimate
        fields = ['id', 'name', 'description', 'template_code', 'order_quantities']


class ProductEstimateInputSerializer(ProductEstimateListSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductEstimate
        fields = ['id', 'product_template', 'order_quantities', 
            'material_spoilage_rate']

    def create(self, validated_data):
        product_template = validated_data.get('product_template')
        order_quantities = validated_data.get('order_quantities')
        material_spoilage_rate = validated_data.get('material_spoilage_rate')
        product_estimate = ProductEstimate.objects.create_product_estimate(
                product_template, order_quantities, material_spoilage_rate)
        return product_estimate

    def update(self, instance, validated_data):
        order_quantities = validated_data.get('order_quantities')
        material_spoilage_rate = validated_data.get('material_spoilage_rate')
        instance.set_estimate_quantities(order_quantities)
        instance.set_material_spoilage_rate(material_spoilage_rate)
        return instance


class ProductEstimateEstimatesSerializer(serializers.Serializer):
    material_estimates = MaterialSerializer(many=True, required=False, read_only=True)
    service_estimates = ServiceEstimateSerializer(many=True, required=False, read_only=True)


class ProductEstimateSummaryPriceSerializer(serializers.Serializer):
    order_quantity = serializers.IntegerField()
    price = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
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

    class Meta:
        model = ProductEstimate
        fields = ['id', 'name', 'description', 'template_code', 
            'summary', 'estimates']