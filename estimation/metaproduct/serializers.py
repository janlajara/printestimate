from rest_framework import serializers
from estimation.process.serializers import OperationListSerializer
from estimation.metaproduct.models import MetaProduct, MetaService, MetaComponent, \
    MetaProperty, MetaPropertyOption, MetaMaterialOption


class MetaProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaProduct
        fields = ['id', 'name', 'description']


class MetaPropertyOptionSerializer(serializers.ModelSerializer):
    # operation = OperationListSerializer()
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = MetaPropertyOption
        fields = ['id', 'label', 'operation']


class MetaPropertySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    meta_property_options = MetaPropertyOptionSerializer(many=True)

    class Meta:
        model = MetaProperty
        fields = ['id', 'name', 'options_type', 'is_required', 
            'meta_property_options']


class MetaMaterialOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = MetaMaterialOption
        fields = ['id', 'label', 'item']


class MetaComponentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaComponent
        fields = ['id', 'name', 'type']    


class MetaComponentWriteSerializer(serializers.ModelSerializer):
    meta_properties = MetaPropertySerializer(many=True)
    meta_material_options = MetaMaterialOptionSerializer(many=True)

    class Meta:
        model = MetaComponent
        fields = ['id', 'name', 'type', 'meta_material_options', 'meta_properties']


class MetaServiceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaService
        fields = ['id', 'name', 'type', 'costing_measure']


class MetaServiceWriteSerializer(serializers.ModelSerializer):
    meta_properties = MetaPropertySerializer(many=True)

    class Meta:
        model = MetaService
        fields = ['id', 'name', 'type', 'costing_measure', 'meta_properties']