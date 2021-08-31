from rest_framework import serializers
from estimation.process.serializers import OperationListSerializer
from estimation.metaproduct.models import MetaProduct, MetaService, MetaComponent, \
    MetaOperation, MetaComponentOperation, MetaOperationOption, MetaMaterialOption, MetaMachineOption


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

    class Meta:
        model = MetaMaterialOption
        fields = ['id', 'label', 'item', 'type']


class MetaMachineOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    label = serializers.CharField(read_only=True)

    class Meta:
        model = MetaMachineOption
        fields = ['id', 'label', 'machine']


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