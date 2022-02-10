from json import JSONEncoder
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from djmoney.contrib.django_rest_framework import MoneyField
from inventory.models import Item
from estimation.product.models import ProductEstimate, \
    EstimateQuantity, Product, Component, Service, \
    Material, TapeMaterial, LineMaterial, \
    PaperMaterial, PanelMaterial, LiquidMaterial

'''
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['material_id', 'component', 'name', 'item']


class LineMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineMaterial
        fields = ['material_id', 'component', 'name', 'item',
            'length_value', 'length_uom']


class TapeMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TapeMaterial
        fields = ['material_id', 'component', 'name', 'item', 
            'length_value', 'length_uom', 'width_value', 'width_uom']

    def validate(self, data):
        errors = {}
        if data.get('length_value', None) is not None and data.get('length_uom', None) is None:
            errors['length_uom'] = 'Must provide value if length_value is populated'
        if data.get('width_value', None) is not None and data.get('width_uom', None) is None:
            errors['width_uom'] = 'Must provide value if width_value is populated'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class PaperMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperMaterial
        fields = ['material_id', 'component', 'name', 'item',
            'width_value', 'length_value', 'size_uom', 'gsm', 'finish', 'estimates']


class PanelMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanelMaterial
        fields = ['material_id', 'component', 'name', 'item',
            'width_value', 'length_value', 'size_uom', 'thickness_value', 'thickness_uom']


class LiquidMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidMaterial
        fields = ['material_id', 'component', 'name', 'item',
            'volume_value', 'volume_uom']


class MaterialPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Material: MaterialSerializer,
        LineMaterial: LineMaterialSerializer,
        TapeMaterial: TapeMaterialSerializer,
        PaperMaterial: PaperMaterialSerializer,
        PanelMaterial: PanelMaterialSerializer,
        LiquidMaterial: LiquidMaterialSerializer
    }
    
    def to_resource_type(self, model_or_instance):
        mapping = {
            LineMaterial.__name__: Item.LINE,
            TapeMaterial.__name__: Item.TAPE,
            PaperMaterial.__name__: Item.PAPER,
            PanelMaterial.__name__: Item.PANEL,
            LiquidMaterial.__name__: Item.LIQUID,
            Material.__name__: Item.OTHER
        }
        object_name = model_or_instance._meta.object_name
        resource_type = mapping.get(object_name, 'other')
        return resource_type
'''

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


class ActivityExpenseEstimateEstimateSerializer(serializers.Serializer):
    uom = serializers.CharField()
    type = serializers.CharField()
    rate = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')
    order_quantity = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(default=0, max_digits=None,  decimal_places=2)
    cost = MoneyField(max_digits=14, decimal_places=2, read_only=False, 
        default_currency='PHP')


class ActivityExpenseEstimateSerializer(serializers.Serializer):
    name = serializers.CharField()
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
    operation_estimates = OperationEstimateSerializer(many=True, read_only=True)


class ProductEstimateListSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    product_template_code = serializers.SerializerMethodField()
    order_quantities = serializers.ListField(child=serializers.IntegerField(), 
        read_only=True)

    class Meta:
        model = ProductEstimate
        fields = ['id', 'product_name', 'product_template_code', 
            'product_description', 'order_quantities']

    def get_product_name(self, instance):
        return instance.product.name

    def get_product_description(self, instance):
        return instance.product.description

    def get_product_template_code(self, instance):
        return instance.product_template.code


class ProductEstimateInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    product_template_id = serializers.IntegerField()
    order_quantities = serializers.ListField(child=serializers.IntegerField(min_value = 1))


class ProductEstimateOutputSerializer(ProductEstimateInputSerializer):
    material_estimates = MaterialSerializer(many=True, required=False, read_only=True)
    service_estimates = ServiceEstimateSerializer(many=True, required=False, read_only=True)