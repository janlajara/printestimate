from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from inventory.models import Item
from estimation.template.models import ProductTemplate, ComponentTemplate, \
    MaterialTemplate, ServiceTemplate, OperationTemplate, OperationOptionTemplate, \
    TapeComponentTemplate, LineComponentTemplate, PaperComponentTemplate, \
    PanelComponentTemplate, LiquidComponentTemplate
from estimation.metaproduct.models import MetaProduct, MetaComponent, MetaMaterialOption, \
    MetaService, MetaOperationOption
from estimation.metaproduct.serializers import MetaProductSerializer, MetaComponentSerializer, \
    MetaMaterialOptionSerializer, MetaServiceSerializer, MetaOperationSerializer, \
    MetaOperationOptionSerializer


class OperationOptionTemplate(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = OperationOptionTemplate
        fields = ['id', 'label', 'meta_operation_option']


class OperationTemplateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    operation_option_templates = OperationOptionTemplate(many=True)

    class Meta:
        model = OperationTemplate
        fields = ['id', 'name', 'meta_operation', 'operation_option_templates']


class OperationTemplateReadSerializer(serializers.ModelSerializer):
    meta_operation_option = MetaOperationSerializer(read_only=True)


class ServiceTemplateSerializer(serializers.ModelSerializer):
    operation_templates = OperationTemplateSerializer(many=True)

    class Meta:
        model = ServiceTemplate
        fields = ['id', 'name', 'type', 'meta_service', 'operation_templates']


class ServiceTemplateReadSerializer(ServiceTemplateSerializer):
    meta_service = MetaServiceSerializer(read_only=True)


class MaterialTemplateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = MaterialTemplate
        fields = ['id', 'label', 'quantity', 
            'meta_material_option']


class MaterialTemplateReadSerializer(serializers.ModelSerializer):
    meta_material_option = MetaMaterialOptionSerializer(read_only=True)


class ComponentTemplateSerializer(serializers.ModelSerializer):
    material_templates = MaterialTemplateSerializer(many=True)

    class Meta:
        model = ComponentTemplate
        fields = ['component_template_id', 'name', 'type', 
            'quantity', 'total_material_quantity', 
            'meta_component', 'material_templates',
            'machine_option']


class LineComponentTemplateSerializer(ComponentTemplateSerializer):
    class Meta:
        model = LineComponentTemplate
        fields = ['component_template_id', 'name', 'type', 
            'quantity', 'total_material_quantity', 
            'meta_component', 'machine_option', 'material_templates',
            'length_value', 'length_uom']

    def validate(self, data):
        errors = {}
        if data.get('length_value', None) is not None and data.get('length_uom', None) is None:
            errors['length_uom'] = 'Must provide value if length_value is populated'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class TapeComponentTemplateSerializer(ComponentTemplateSerializer):
    class Meta:
        model = TapeComponentTemplate
        fields = ['component_template_id', 'name', 'type', 
            'quantity', 'total_material_quantity', 
            'meta_component', 'machine_option', 'material_templates',
            'length_value', 'length_uom', 
            'width_value', 'width_uom']

    def validate(self, data):
        errors = {}
        if data.get('length_value', None) is not None and data.get('length_uom', None) is None:
            errors['length_uom'] = 'Must provide value if length_value is populated'
        if data.get('width_value', None) is not None and data.get('width_uom', None) is None:
            errors['width_uom'] = 'Must provide value if width_value is populated'

        if errors:
            raise serializers.ValidationError(errors)

        return data


class PaperComponentTemplateSerializer(ComponentTemplateSerializer):
    class Meta:
        model = PaperComponentTemplate
        fields = ['component_template_id', 'name', 'type', 
            'quantity', 'total_material_quantity', 
            'meta_component', 'machine_option', 'material_templates',
            'width_value', 'length_value', 'size_uom']


class PanelComponentTemplateSerializer(ComponentTemplateSerializer):
    class Meta:
        model = PanelComponentTemplate
        fields = ['component_template_id', 'name', 'type', 
            'quantity', 'total_material_quantity', 
            'meta_component', 'machine_option', 'material_templates',
            'width_value', 'length_value', 'size_uom']

    #def validate(self, data):
    #    if data.get('thickness_value', None) is not None and data.get('thickness_uom', None) is None:
    #        raise serializers.ValidationError(
    #            {'thickness_uom': 'Must provide value if thickness_value is populated'})
    #    return data


class LiquidComponentTemplateSerializer(ComponentTemplateSerializer):
    class Meta:
        model = LiquidComponentTemplate
        fields = ['component_template_id', 'name', 'type', 
            'quantity', 'total_material_quantity', 
            'meta_component', 'machine_option', 'material_templates',
            'volume_value', 'volume_uom']

    def validate(self, data):
        errors = {}
        if data.get('volume_value', None) is not None and data.get('volume_uom', None) is None:
            errors['volume_uom'] = 'Must provide value if volume_value is populated'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class ComponentTemplatePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ComponentTemplate: ComponentTemplateSerializer,
        LineComponentTemplate: LineComponentTemplateSerializer,
        TapeComponentTemplate: TapeComponentTemplateSerializer,
        PaperComponentTemplate: PaperComponentTemplateSerializer,
        PanelComponentTemplate: PanelComponentTemplateSerializer,
        LiquidComponentTemplate: LiquidComponentTemplateSerializer,
    }

    @classmethod
    def get_serializer_class(cls, resourcetype):
        clazz = ComponentTemplate.objects.get_class(resourcetype)
        serializer_class = cls.model_serializer_mapping.get(clazz, ComponentTemplateSerializer)
        return serializer_class

    def to_resource_type(self, model_or_instance):
        mapping = {
            LineComponentTemplate.__name__: Item.LINE,
            TapeComponentTemplate.__name__: Item.TAPE,
            PaperComponentTemplate.__name__: Item.PAPER,
            PanelComponentTemplate.__name__: Item.PANEL,
            LiquidComponentTemplate.__name__: Item.LIQUID,
            ComponentTemplate.__name__: Item.OTHER
        }
        object_name = model_or_instance._meta.object_name
        resource_type = mapping.get(object_name, 'other')
        return resource_type


class ComponentTemplateReadSerializer(ComponentTemplateSerializer):
    meta_component = MetaComponentSerializer(read_only=True)


class ProductTemplateSerializer(serializers.ModelSerializer):
    component_templates = ComponentTemplatePolymorphicSerializer(many=True)
    service_templates = ServiceTemplateSerializer(many=True)

    class Meta:
        model = ProductTemplate
        fields = ['id', 'name', 'description', 'meta_product',
            'component_templates', 'service_templates']


class ProductTemplateListSerializer(serializers.ModelSerializer):
    meta_product = MetaProductSerializer(read_only=True)

    class Meta:
        model = ProductTemplate
        fields = ['id', 'name', 'description', 'meta_product']