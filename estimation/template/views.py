from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.template import serializers
from estimation.template.models import ProductTemplate, ComponentTemplate, \
    MaterialTemplate, ServiceTemplate, OperationTemplate, OperationOptionTemplate


class ProductTemplateViewUtils:

    @classmethod
    def save_component_templates(cls, product_template, component_templates_data):
        existing_ids = [m.get('component_template_id') for m in component_templates_data
            if not m.get('component_template_id') is None]
        ids_to_delete = [m.component_template_id for m in ComponentTemplate.objects.filter(
            product_template__pk=product_template.pk)
            if m is not None and m.component_template_id not in existing_ids]
        ComponentTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for ct_data in component_templates_data:
            resourcetype = ct_data.pop('resourcetype')
            material_templates_data = ct_data.pop('material_templates')
            ct = product_template.add_component_template(**ct_data)
            cls.save_material_templates(ct, material_templates_data)

    @classmethod
    def save_material_templates(cls, component_template, material_templates_data):
        existing_ids = [m.get('id') for m in material_templates_data
            if not m.get('id') is None]
        ids_to_delete = [m.id for m in MaterialTemplate.objects.filter(
            component_template__pk=component_template.pk)
            if m is not None and m.id not in existing_ids]
        MaterialTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for mt_data in material_templates_data:
            mt_id = mt_data.pop('id') if 'id' in mt_data else None

            if mt_id is not None:
                MaterialTemplate.objects.filter(pk=mt_id).update(**mt_data)
            else:
                mmo = component_template.add_material_template(**mt_data)

    @classmethod
    def save_service_templates(cls, product_template, service_templates_data):
        existing_ids = [m.get('id') for m in service_templates_data if not m.get('id') is None]
        ids_to_delete = [m.id for m in ServiceTemplate.objects.filter(
            product_template__pk=product_template.pk)
            if m is not None and m.id not in existing_ids]
        ServiceTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for st_data in service_templates_data:
            operation_templates_data = st_data.pop('operation_templates')
            st = product_template.add_service_template(**st_data)
            cls.save_operation_templates(st, operation_templates_data)

    @classmethod
    def save_operation_templates(cls, service_template, operation_templates_data):
        existing_ids = [m.get('id') for m in operation_templates_data if not m.get('id') is None]
        ids_to_delete = [m.id for m in OperationTemplate.objects.filter(
            service_template__pk=service_template.pk)
            if m is not None and m.id not in existing_ids]
        OperationTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for ot_data in operation_templates_data:
            operation_option_templates_data = ot_data.pop('operation_option_templates')
            ot_id = ot_data.pop('id') if 'id' in ot_data else None

            if ot_id is not None:
                OperationTemplate.objects.filter(pk=ot_id).update(**ot_data)
            else:
                operation_template = service_template.add_operation_template(**ot_data)
                cls.save_operation_option_templates(operation_template, 
                    operation_option_templates_data)

    @classmethod
    def save_operation_option_templates(cls, operation_template, operation_option_templates_data):
        existing_ids = [m.get('id') for m in operation_option_templates_data
            if not m.get('id') is None]
        ids_to_delete = [m.id for m in OperationOptionTemplate.objects.filter(
            operation_template__pk=operation_template.pk)
            if m is not None and m.id not in existing_ids]
        OperationOptionTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for oot_data in operation_option_templates_data:
            oot_id = oot_data.pop('id') if 'id' in oot_data else None
            if oot_id is not None:
                OperationOptionTemplate.objects.filter(pk=oot_id).update(**oot_data)
            else:
                operation_template.add_operation_option_template(**oot_data)


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

            component_templates = ProductTemplateViewUtils.save_component_templates(
                product_template, component_templates_data)

            service_templates = ProductTemplateViewUtils.save_service_templates(
                product_template, service_templates_data)

            serialized = serializers.ProductTemplateSerializer(product_template)
            return Response(serialized.data)
        else:
            return Response({'errors': deserialized.errors}, status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        if pk is not None:
            deserialized = serializers.ProductTemplateSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                component_templates_data = validated_data.pop('component_templates', None)
                service_templates_data = validated_data.pop('service_templates', None)
                product_template = get_object_or_404(ProductTemplate, pk=pk)

                ProductTemplate.objects.filter(pk=pk).update(**validated_data)
                ProductTemplateViewUtils.save_component_templates(
                    product_template, component_templates_data)
                ProductTemplateViewUtils.save_service_templates(
                    product_template, service_templates_data)

                product_template.refresh_from_db()
                serialized = serializers.ProductTemplateSerializer(product_template)
                return Response(serialized.data)
                
                return Response(serialized.data)
            else:
                return Response({'errors': deserialized.errors},
                    status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': 'component template pk is not provided'},
                status.HTTP_400_BAD_REQUEST)

'''
class ComponentTemplateViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ComponentTemplate.objects.all()
    serializer_class = serializers.ComponentTemplateSerializer

    def update_material_templates(self, component_template, material_templates_data):
        existing_ids = [m.get('id') for m in material_templates_data
            if not m.get('id') is None]
        ids_to_delete = [m.id for m in MaterialTemplate.objects.filter(component_template__pk=component_template.pk)
            if m is not None and m.id not in existing_ids]
        MaterialTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for mt_data in material_templates_data:
            mt_id = mt_data.pop('id') if 'id' in mt_data else None
            if mt_id is not None:
                MaterialTemplate.objects.filter(pk=mt_id).update(**mt_data)
            else:
                component_template.add_material_template(**mt_data)

    def update(self, request, pk=None):
        if pk is not None:
            deserialized = serializers.ComponentTemplateSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                component_template = get_object_or_404(ComponentTemplate, pk=pk)
                material_templates_data = validated_data.pop('material_templates')
                self.update_material_templates(component_template, material_templates_data)
                
                ComponentTemplate.objects.filter(pk=pk).update(**validated_data)
                component_template.refresh_from_db()
                serialized = serializers.ComponentTemplateSerializer(component_template)
                return Response(serialized.data)
            else:
                return Response({'errors': deserialized.errors},
                    status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': 'component template pk is not provided'},
                status.HTTP_400_BAD_REQUEST)


class ServiceTemplateViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = ServiceTemplate.objects.all()
    serializer_class = serializers.ServiceTemplateSerializer

    def update_operation_option_templates(self, operation_template, operation_option_templates_data):
        existing_ids = [m.get('id') for m in operation_option_templates_data
            if not m.get('id') is None]
        ids_to_delete = [m.id for m in OperationOptionTemplate.objects.filter(pk=operation_template.pk)
            if m is not None and m.id not in existing_ids]
        OperationOptionTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for oot_data in operation_option_templates_data:
            oot_id = oot_data.pop('id') if 'id' in oot_data else None
            if oot_id is not None:
                OperationOptionTemplate.objects.filter(pk=oot_id).update(**oot_data)
            else:
                operation_template.add_operation_option_template(**oot_data)

    def update_operation_templates(self, service_template, operation_templates_data):
        existing_ids = [m.get('id') for m in operation_templates_data
            if not m.get('id') is None]
        ids_to_delete = [m.id for m in OperationTemplate.objects.filter(pk=service_template.pk)
            if m is not None and m.id not in existing_ids]
        OperationTemplate.objects.filter(pk__in=ids_to_delete).delete()

        for ot_data in operation_templates_data:
            ootemplates_data = ot_data.pop('operation_option_templates')
            operation_template = None

            ot_id = ot_data.pop('id') if 'id' in ot_data else None
            if ot_id is not None:
                OperationTemplate.objects.filter(pk=ot_id).update(**ot_data)
                operation_template = OperationTemplate.objects.get(ot_id)
            else:
                operation_template = service_template.add_operation_template(**ot_data)
            self.update_operation_option_templates(operation_template, ootemplates_data)

    def update(self, request, pk=None):
        if pk is not None:
            deserialized = serializers.ServiceTemplateSerializer(data=request.data)
            
            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                service_template = get_object_or_404(ServiceTemplate, pk=pk)
                operation_templates_data = validated_data.pop('operation_templates')
                self.update_operation_templates(service_template, operation_templates_data)

                ServiceTemplate.objects.filter(pk=pk).update(**validated_data)
                service_template.refresh_from_db()

                serialized = serializers.ServiceTemplateSerializer(service_template)
                return Response(serialized.data)
            else:
                return Response({'errors': deserialized.errors},
                    status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': 'service template pk is not provided'},
                status.HTTP_400_BAD_REQUEST)
'''