from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from inventory.models import Item
from estimation.product.models import Material, TapeMaterial, LineMaterial, \
    PaperMaterial, PanelMaterial, LiquidMaterial


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
            'width_value', 'length_value', 'size_uom', 'gsm', 'finish']


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