from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.template import serializers
from estimation.template.models import ProductTemplate


class ProductTemplateViewUtils:

    @classmethod
    def create_component_templates(cls, product_template, component_templates_data):
        component_templates = []
        for ct_data in component_templates_data:
            resourcetype = ct_data.pop('resourcetype')
            material_templates_data = ct_data.pop('material_templates')
            ct = product_template.add_component_template(**ct_data)
            cls.create_material_templates(ct, material_templates_data)

            component_templates.append(ct)
        return component_templates

    @classmethod
    def create_material_templates(cls, component_template, material_templates_data):
        material_templates = []
        for mt_data in material_templates_data:
            mmo = component_template.add_material_template(**mt_data)
            material_templates.append(mmo)
        return material_templates

    @classmethod
    def create_service_templates(cls, product_template, service_templates_data):
        service_templates = []
        for st_data in service_templates_data:
            operation_templates_data = st_data.pop('operation_templates')
            st = product_template.add_service_template(**st_data)
            cls.create_operation_templates(st, operation_templates_data)

            service_templates.append(st)
        return service_templates

    @classmethod
    def create_operation_templates(cls, service_template, operations_template_data):
        operation_templates = []
        for ot_data in operations_template_data:
            operation_option_templates_data = ot_data.pop('operation_option_templates')
            ot = service_template.add_operation_template(**ot_data)
            cls.create_operation_option_templates(ot, operation_option_templates_data)

            operation_templates.append(ot)
        return operation_templates

    @classmethod
    def create_operation_option_templates(cls, operation_template, operation_option_templates_data):
        operation_option_templates = []
        for oot_data in operation_option_templates_data:
            oot = operation_template.add_operation_option_template(**oot_data)
            operation_option_templates.append(oot)
        return operation_option_templates


class ProductTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProductTemplate.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'retrieve']:
            return serializers.ProductTemplateSerializer
        else:
            return serializers.ProductTemplateListSerializer

    def create(self, request):
        deserialized = serializers.ProductTemplateSerializer(data=request.data)

        if deserialized.is_valid():
            validated_data = deserialized.validated_data
            component_templates_data = validated_data.pop('component_templates', None)
            service_templates_data = validated_data.pop('service_templates', None)

            product_template = ProductTemplate.objects.create(**validated_data)

            component_templates = ProductTemplateViewUtils.create_component_templates(
                product_template, component_templates_data)

            _create_service_templates = ProductTemplateViewUtils.create_service_templates(
                product_template, service_templates_data)

            serialized = serializers.ProductTemplateSerializer(product_template)
            return Response(serialized.data)
        else:
            return Response({'errors': deserialized.errors}, status.HTTP_400_BAD_REQUEST)