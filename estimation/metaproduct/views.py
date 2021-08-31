from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.metaproduct.models import MetaProduct, MetaComponent, MetaService, \
     MetaOperation, MetaComponentOperation, MetaOperationOption, MetaMaterialOption, MetaMachineOption
from estimation.metaproduct import serializers

# Create your views here.
class MetaProductViewSet(viewsets.ModelViewSet):
    queryset = MetaProduct.objects.all()
    serializer_class = serializers.MetaProductSerializer


class MetaOperationViewUtils:

    @classmethod
    def create_meta_operation_options(cls, meta_operation, meta_operation_options):
        for mpo_data in meta_operation_options:
            meta_operation.add_option(**mpo_data)

    @classmethod
    def create_meta_operations(cls, obj, meta_operations):
        for mp_data in meta_operations:
            meta_operation_options = mp_data.pop('meta_operation_options')
            meta_operation = obj.add_meta_operation(**mp_data)
            cls.create_meta_operation_options(meta_operation, meta_operation_options)

    @classmethod
    def update_or_create_meta_operation_options(cls, meta_operation, meta_operation_options):
        existing_ids = [y.get('id') for y in meta_operation_options if not y.get('id') is None]
        ids_to_delete = [x.id for x in meta_operation.options if x is not None and not x.id in existing_ids]

        MetaOperationOption.objects.filter(pk__in=ids_to_delete).delete()

        for mpo_data in meta_operation_options:
            mpo_id = mpo_data.pop('id') if 'id' in mpo_data else None

            if mpo_id is None:
                meta_operation.add_option(**mpo_data)
            else:
                MetaOperationOption.objects.filter(pk=mpo_id).update(**mpo_data)

    @classmethod
    def update_or_create_meta_operations(cls, obj, meta_operations):
        existing_ids = [y.get('id') for y in meta_operations if not y.get('id') is None]
        ids_to_delete = [x.id for x in obj.meta_operations.all() if x is not None and not x.id in existing_ids]

        MetaOperation.objects.filter(pk__in=ids_to_delete).delete()

        for mp_data in meta_operations:
            meta_operation_options = mp_data.pop('meta_operation_options')
            mp_id = mp_data.pop('id') if 'id' in mp_data else None
            meta_operation = None
            
            if mp_id is None:
                meta_operation = obj.add_meta_operation(**mp_data)
            else:
                if isinstance(obj, MetaComponent):
                    MetaComponentOperation.objects.filter(pk=mp_id).update(**mp_data)
                else:
                    MetaOperation.objects.filter(pk=mp_id).update(**mp_data)
                meta_operation = MetaOperation.objects.get(pk=mp_id)
    
            cls.update_or_create_meta_operation_options(meta_operation, meta_operation_options)


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
    
    def create_meta_machine_options(self, meta_component, meta_machine_options):
        for mmo_data in meta_machine_options:
            mmo_data.pop('id')
            meta_component.add_meta_machine_option(**mmo_data)    

    def create(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            deserialized = serializers.MetaComponentSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_operations = validated_data.pop('meta_operations')
                meta_material_options = validated_data.pop('meta_material_options')
                meta_machine_options = validated_data.pop('meta_machine_options')
                meta_component = meta_product.add_meta_component(**validated_data)
                MetaOperationViewUtils.create_meta_operations(meta_component, meta_operations)
                self.create_meta_material_options(meta_component, meta_material_options)
                self.create_meta_machine_options(meta_component, meta_machine_options)

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
            return MetaService.objects.filter(meta_product__pk=pk).order_by('sequence')
        else:
            return MetaService.objects.all()

    def create(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            deserialized = serializers.MetaServiceSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_operations = validated_data.pop('meta_operations')
                meta_service = meta_product.add_meta_service(**validated_data)
                MetaOperationViewUtils.create_meta_operations(meta_service, meta_operations)

                serialized = serializers.MetaServiceSerializer(meta_service)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'missing metaproduct pk'}, status.HTTP_400_BAD_REQUEST)


class MetaProductServiceUpdateSequenceView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = MetaComponent.objects.all()
    serializer_class = serializers.MetaServiceSequenceSerializer

    def update(self, request, pk=None):
        if pk is not None:
            meta_product = get_object_or_404(MetaProduct, pk=pk)
            related_ids = [x.id for x in meta_product.meta_product_datas.all()]
            deserialized = serializers.MetaServiceSequenceSerializer(data=request.data, 
                many=True)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data 
                filtered = [data for data in validated_data if data.get('id') in related_ids]
                for service_data in filtered:
                    service_id = service_data.get('id')
                    service_sequence = service_data.get('sequence')
                    MetaService.objects.filter(pk=service_id).update(sequence=service_sequence)

                meta_services = MetaService.objects.filter(pk__in=related_ids)
                serialized = serializers.MetaServiceSequenceSerializer(meta_services, many=True)
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
        ids_to_delete = [x.id for x in meta_component.meta_material_options.all() if x is not None and not x.id in existing_ids]

        MetaMaterialOption.objects.filter(pk__in=ids_to_delete).delete()

        for mmo_data in meta_material_options:
            mmo_id = mmo_data.pop('id') if 'id' in mmo_data else None
            if mmo_id is None:
                meta_component.add_meta_material_option(**mmo_data)
            else:
                MetaMaterialOption.objects.filter(pk=mmo_id).update(**mmo_data)

    def update_or_create_meta_machine_options(self, meta_component, meta_machine_options):
        existing_ids = [y.get('id') for y in meta_machine_options if not y.get('id') is None]
        ids_to_delete = [x.id for x in meta_component.meta_machine_options.all() if x is not None and not x.id in existing_ids]

        MetaMachineOption.objects.filter(pk__in=ids_to_delete).delete()

        for mmc_data in meta_machine_options:
            mmc_id = mmc_data.pop('id') if 'id' in mmc_data else None
            if mmc_id is None:
                meta_component.add_meta_machine_option(**mmc_data)
            else:
                MetaMachineOption.objects.filter(pk=mmc_id).update(**mmc_data)

    def update(self, request, pk=None):
        if pk is not None:
            meta_component = get_object_or_404(MetaComponent, pk=pk)
            deserialized = serializers.MetaComponentSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                meta_operations = validated_data.pop('meta_operations')
                meta_material_options = validated_data.pop('meta_material_options')
                meta_machine_options = validated_data.pop('meta_machine_options')
                MetaOperationViewUtils.update_or_create_meta_operations(meta_component, meta_operations)
                self.update_or_create_meta_material_options(meta_component, meta_material_options)
                self.update_or_create_meta_machine_options(meta_component, meta_machine_options)

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
                meta_operations = validated_data.pop('meta_operations')
                MetaOperationViewUtils.update_or_create_meta_operations(meta_service, meta_operations)
                
                if validated_data.get('meta_component') is None:
                    validated_data['estimate_variable_type'] = None

                MetaService.objects.filter(pk=pk).update(**validated_data)
                meta_service = get_object_or_404(MetaService, pk=pk)

                serialized = serializers.MetaServiceSerializer(meta_service)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'missing metaservice pk'}, status.HTTP_400_BAD_REQUEST)