from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.metaproduct.models import MetaProduct, MetaComponent, \
    MetaService, MetaProperty, MetaComponentProperty, MetaPropertyOption, MetaMaterialOption
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
        ids_to_delete = [x.id for x in meta_property.options if x is not None and not x.id in existing_ids]

        MetaPropertyOption.objects.filter(pk__in=ids_to_delete).delete()

        for mpo_data in meta_property_options:
            mpo_id = mpo_data.pop('id') if 'id' in mpo_data else None

            if mpo_id is None:
                meta_property.add_option(**mpo_data)
            else:
                MetaPropertyOption.objects.filter(pk=mpo_id).update(**mpo_data)

    @classmethod
    def update_or_create_meta_properties(cls, obj, meta_properties):
        existing_ids = [y.get('id') for y in meta_properties if not y.get('id') is None]
        ids_to_delete = [x.id for x in obj.meta_properties.all() if x is not None and not x.id in existing_ids]

        MetaProperty.objects.filter(pk__in=ids_to_delete).delete()

        for mp_data in meta_properties:
            meta_property_options = mp_data.pop('meta_property_options')
            mp_id = mp_data.pop('id') if 'id' in mp_data else None
            meta_property = None
            
            if mp_id is None:
                meta_property = obj.add_meta_property(**mp_data)
            else:
                if isinstance(obj, MetaComponent):
                    MetaComponentProperty.objects.filter(pk=mp_id).update(**mp_data)
                else:
                    MetaProperty.objects.filter(pk=mp_id).update(**mp_data)
                meta_property = MetaProperty.objects.get(pk=mp_id)
    
            cls.update_or_create_meta_property_options(meta_property, meta_property_options)


class MetaProductComponentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):
    serializer_class = serializers.MetaComponentSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return MetaComponent.objects.filter(meta_product__pk=pk)
        else:
            return MetaComponent.objects.all()

    def create_meta_material_options(self, meta_component, meta_material_options):
        for mmo_data in meta_material_options:
            mmo_data.pop('id')
            meta_component.add_meta_material_option(**mmo_data)

    def create(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            deserialized = serializers.MetaComponentSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                meta_material_options = validated_data.pop('meta_material_options')
                meta_component = meta_product.add_meta_component(**validated_data)
                MetaPropertyViewUtils.create_meta_properties(meta_component, meta_properties)
                self.create_meta_material_options(meta_component, meta_material_options)

                serialized = serializers.MetaComponentSerializer(meta_component)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'missing metaproduct pk'}, status.HTTP_400_BAD_REQUEST)


class MetaProductServiceViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, 
                                viewsets.GenericViewSet):
    serializer_class = serializers.MetaServiceSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return MetaService.objects.filter(meta_product__pk=pk)
        else:
            return MetaService.objects.all()

    def create(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            deserialized = serializers.MetaServiceSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                meta_service = meta_product.add_meta_service(**validated_data)
                MetaPropertyViewUtils.create_meta_properties(meta_service, meta_properties)

                serialized = serializers.MetaServiceSerializer(meta_service)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'missing metaproduct pk'}, status.HTTP_400_BAD_REQUEST)


class MetaComponentViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, 
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = MetaComponent.objects.all()
    serializer_class = serializers.MetaComponentSerializer

    def update_or_create_meta_material_options(self, meta_component, meta_material_options):
        existing_ids = [y.get('id') for y in meta_material_options if not y.get('id') is None]
        ids_to_delete = [x.id for x in meta_component.meta_material_options.all() if not x is not None and x.id in existing_ids]

        MetaMaterialOption.objects.filter(pk__in=ids_to_delete).delete()

        for mmo_data in meta_material_options:
            mmo_id = mmo_data.pop('id') if 'id' in mmo_data else None
            if mmo_id is None:
                meta_component.add_meta_material_option(**mmo_data)
            else:
                MetaMaterialOption.objects.filter(pk=mmo_id).update(**mmo_data)

    def update(self, request, pk=None):
        if pk is not None:

            meta_component = get_object_or_404(MetaComponent, pk=pk)
            deserialized = serializers.MetaComponentSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                meta_material_options = validated_data.pop('meta_material_options')
                MetaPropertyViewUtils.update_or_create_meta_properties(meta_component, meta_properties)
                self.update_or_create_meta_material_options(meta_component, meta_material_options)

                MetaComponent.objects.filter(pk=pk).update(**validated_data)
                meta_component = get_object_or_404(MetaComponent, pk=pk)

                serialized = serializers.MetaComponentSerializer(meta_component)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'missing metacomponent pk'}, status.HTTP_400_BAD_REQUEST)


class MetaServiceViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, 
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = MetaService.objects.all()
    serializer_class = serializers.MetaServiceSerializer

    def update(self, request, pk=None):
        if pk is not None:
            meta_service = get_object_or_404(MetaService, pk=pk)
            deserialized = serializers.MetaServiceSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_properties = validated_data.pop('meta_properties')
                MetaPropertyViewUtils.update_or_create_meta_properties(meta_service, meta_properties)

                MetaService.objects.filter(pk=pk).update(**validated_data)
                meta_service = get_object_or_404(MetaService, pk=pk)

                serialized = serializers.MetaServiceSerializer(meta_service)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'missing metaservice pk'}, status.HTTP_400_BAD_REQUEST)