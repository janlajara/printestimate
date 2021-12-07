from rest_framework import serializers
from inventory.serializers import ItemPropertiesPolymorphicSerializer
from estimation.process.serializers import OperationListSerializer
from estimation.metaproduct.models import MetaProduct, MetaService, MetaComponent, \
    MetaOperation, MetaComponentOperation, MetaOperationOption, MetaMaterialOption, MetaMachineOption
from estimation.machine.serializers import MachinePolymorphicSerializer

class MetaProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaProduct
        fields = ['id', 'name', 'description']


class MetaOperationOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    label = serializers.CharField(read_only=True)

    class Meta:
        model = MetaOperationOption
        fields = ['id', 'label', 'operation']


class MetaOperationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    meta_operation_options = MetaOperationOptionSerializer(many=True)

    class Meta:
        model = MetaOperation
        fields = ['id', 'name', 'options_type', 'is_required', 
            'meta_operation_options']


class MetaComponentOperationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    meta_operation_options = MetaOperationOptionSerializer(many=True)
    
    class Meta:
        model = MetaComponentOperation
        fields = ['id', 'name', 'options_type', 'costing_measure', 
            'is_required', 'meta_operation_options']


class MetaMaterialOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    label = serializers.CharField(read_only=True) 
    type = serializers.CharField(read_only=True)
    properties = serializers.SerializerMethodField()

    class Meta:
        model = MetaMaterialOption
        fields = ['id', 'label', 'item', 'type', 'properties']

    def get_properties(self, obj):
        if obj.item is not None:
            serializer = ItemPropertiesPolymorphicSerializer(obj.item.properties)
            return serializer.data


class MetaMachineOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    label = serializers.CharField(read_only=True)
    machine_obj = serializers.SerializerMethodField()

    class Meta:
        model = MetaMachineOption
        fields = ['id', 'label', 'machine', 'machine_obj']

    def get_machine_obj(self, obj):
        if obj.machine is not None:
            serializer = MachinePolymorphicSerializer(obj.machine)
            return serializer.data

class MetaEstimateVariableSerializer(serializers.Serializer):
    type = serializers.CharField()
    costing_measure = serializers.CharField()
    label = serializers.CharField(read_only=True)

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.costing_measure = validated_data.get(
            'costing_measure', instance.costing_measure)
        return instance

    def create(self, validated_data):
        return MetaComponent.MeasurementVariable(**validated_data)


class MetaComponentSerializer(serializers.ModelSerializer):
    meta_operations = MetaComponentOperationSerializer(many=True)
    meta_material_options = MetaMaterialOptionSerializer(many=True)
    meta_machine_options = MetaMachineOptionSerializer(many=True)
    meta_estimate_variables = MetaEstimateVariableSerializer(many=True, read_only=True)
    
    class Meta:
        model = MetaComponent
        fields = ['id', 'name', 'type', 'allow_multiple_materials', 
            'meta_estimate_variables', 'meta_material_options', 
            'meta_machine_options', 'meta_operations']


class MetaServiceSerializer(serializers.ModelSerializer):
    meta_operations = MetaOperationSerializer(many=True)

    class Meta:
        model = MetaService
        fields = ['id', 'sequence', 'name', 'type', 'costing_measure', 'meta_operations',
            'meta_component', 'estimate_variable_type']


class MetaServiceSequenceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = MetaService
        fields = ['id', 'sequence']