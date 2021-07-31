from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from estimation.metaproduct.models import MetaProduct, MetaComponent, \
    MetaService, MetaProperty, MetaPropertyOption, MetaMaterialOption
from estimation.metaproduct import serializers

# Create your views here.
class MetaProductViewSet(viewsets.ModelViewSet):
    queryset = MetaProduct.objects.all()
    serializer_class = serializers.MetaProductSerializer


class MetaPropertyViewUtils:

    @classmethod
    def create_meta_property_options(cls, meta_property, meta_property_options):
        for mpo_data in meta_property_options:
            meta_property.add_option(**mpo_data)

    @classmethod
    def create_meta_properties(cls, obj, meta_properties):
        for mp_data in meta_properties:
            meta_property_options = mp_data.pop('meta_property_options')
            meta_property = obj.add_meta_property(**mp_data)
            cls.create_meta_property_options(meta_property, meta_property_options)

    @classmethod
    def update_or_create_meta_property_options(cls, meta_property, meta_property_options):
        existing_ids = [y.get('id') for y in meta_property_options if not y.get('id') is None]
        ids_to_delete = [x.id for x in meta_property.options if not x.id in existing_ids]

        MetaPropertyOption.objects.filter(pk__in=ids_to_delete).delete()

        for mpo_data in meta_property_options:
            mpo_id = mpo_data.pop('id')

            if mpo_id is None:
                meta_property.add_option(**mpo_data)
            else:
                MetaPropertyOption.objects.filter(pk=mpo_id).update(**mpo_data)

    @classmethod
    def update_or_create_meta_properties(cls, obj, meta_properties):
        existing_ids = [y.get('id') for y in meta_properties if not y.get('id') is None]
        ids_to_delete = [x.id for x in obj.meta_properties.all() if not x.id in existing_ids]

        MetaProperty.objects.filter(pk__in=ids_to_delete).delete()

        for mp_data in meta_properties:
            meta_property_options = mp_data.pop('meta_property_options')
            mp_id = mp_data.pop('id')
            meta_property = None
            
            if mp_id is None:
                meta_property = obj.add_meta_property(**mp_data)
            else:
                MetaProperty.objects.filter(pk=mp_id).update(**mp_data)
                meta_property = MetaProperty.objects.get(pk=mp_id)
    
            cls.update_or_create_meta_property_options(meta_property, meta_property_options)


class MetaProductComponentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):
    queryset = MetaComponent.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'metadata']:
            return serializers.MetaComponentWriteSerializer
        else:
            return serializers.MetaComponentReadSerializer

    def create_meta_material_options(self, meta_component, meta_material_options):
        for mmo_data in meta_material_options:
            meta_component.add_meta_material_option(**mmo_data)

    def create(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            deserialized = serializers.MetaComponentWriteSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                meta_material_options = validated_data.pop('meta_material_options')
                meta_component = meta_product.add_meta_component(**validated_data)
                MetaPropertyViewUtils.create_meta_properties(meta_component, meta_properties)
                self.create_meta_material_options(meta_component, meta_material_options)

                serialized = serializers.MetaComponentWriteSerializer(meta_component)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing metaproduct pk'})


class MetaProductServiceViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, 
                                viewsets.GenericViewSet):
    queryset = MetaService.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MetaServiceReadSerializer
        else:
            return serializers.MetaServiceWriteSerializer

    def create(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            deserialized = serializers.MetaServiceWriteSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                meta_service = meta_product.add_meta_service(**validated_data)
                MetaPropertyViewUtils.create_meta_properties(meta_service, meta_properties)

                serialized = serializers.MetaServiceWriteSerializer(meta_service)
                return Response(serialized.data)
        else:
            return Response({'error': 'missing metaproduct pk'})


class MetaComponentViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, 
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = MetaComponent.objects.all()
    serializer_class = serializers.MetaComponentWriteSerializer

    def update_or_create_meta_material_options(self, meta_component, meta_material_options):
        existing_ids = [y.get('id') for y in meta_material_options if not y.get('id') is None]
        ids_to_delete = [x.id for x in meta_component.meta_material_options.all() if not x.id in existing_ids]

        MetaMaterialOption.objects.filter(pk__in=ids_to_delete).delete()

        for mmo_data in meta_material_options:
            mmo_id = mmo_data.pop('id')
            if mmo_id is None:
                meta_component.add_meta_material_option(**mmo_data)
            else:
                MetaMaterialOption.objects.filter(pk=mmo_id).update(**mmo_data)

    def update(self, request, pk=None):
        if pk is not None:
            meta_component = get_object_or_404(MetaComponent, pk=pk)
            deserialized = serializers.MetaComponentWriteSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                meta_material_options = validated_data.pop('meta_material_options')
                MetaPropertyViewUtils.update_or_create_meta_properties(meta_component, meta_properties)
                self.update_or_create_meta_material_options(meta_component, meta_material_options)

                MetaComponent.objects.filter(pk=pk).update(**validated_data)
                meta_component = get_object_or_404(MetaComponent, pk=pk)

                serialized = serializers.MetaComponentWriteSerializer(meta_component)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing metacomponent pk'})


class MetaServiceViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, 
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = MetaService.objects.all()
    serializer_class = serializers.MetaServiceWriteSerializer

    def update(self, request, pk=None):
        if pk is not None:
            meta_service = get_object_or_404(MetaService, pk=pk)
            deserialized = serializers.MetaServiceWriteSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                MetaPropertyViewUtils.update_or_create_meta_properties(meta_service, meta_properties)

                MetaService.objects.filter(pk=pk).update(**validated_data)
                meta_service = get_object_or_404(MetaService, pk=pk)

                serialized = serializers.MetaServiceWriteSerializer(meta_service)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing metaservice pk'})