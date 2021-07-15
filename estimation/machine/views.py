from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from estimation.models import Machine, SheetFedPressMachine, ParentSheet, ChildSheet
from estimation import serializers


class MachineTypesViewSet(viewsets.ViewSet):
    def list(self, request):
        types = map(
            lambda x: { "value": x[0], "display": x[1]},
            Machine.TYPES)
        return Response(types)


class SheetFedPressMachineViewSet(viewsets.ModelViewSet):
    queryset = SheetFedPressMachine.objects.all()
    serializer_class = serializers.SheetFedPressMachineSerializer

    def create(self, request):
        deserialized = serializers.SheetFedPressMachineSerializer(data=request.data)

        if deserialized.is_valid():
            validated_data = deserialized.validated_data
            machine = Machine.objects.create_machine(
                type=Machine.SHEET_FED_PRESS, **validated_data)
            serialized = serializers.SheetFedPressMachineSerializer(machine)
            return Response(serialized.data)
        else:
            return Response(deserialized.errors)


class SheetFedPressMachineParentSheetViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ParentSheetSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return ParentSheet.objects.filter(machine=pk)
        else:
            return ParentSheet.objects.all()
    
    def create(self, request, pk=None):
        if pk is not None:
            press_machine = get_object_or_404(SheetFedPressMachine, pk=pk)
            deserialized = serializers.ParentSheetSerializer(data=request.data)

            if deserialized.is_valid():
                try:
                    validated_data = deserialized.validated_data
                    parent_sheet = press_machine.add_parent_sheet(**validated_data)
                    serialized = serializers.ParentSheetSerializer(parent_sheet)
                    return Response(serialized.data)
                except ValueError as ve:
                    return Response({'error': str(ve)})
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': "missing machine pk"})


class SheetFedPressMachineChildSheetViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin, viewsets.GenericViewSet):

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ChildSheetListSerializer
        else:
            return serializers.ChildSheetSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return ChildSheet.objects.filter(parent__machine=pk)
        else:
            return ChildSheet.objects.all()
    
    def create(self, request, pk=None):
        if pk is not None:
            deserialized = serializers.ChildSheetSerializer(data=request.data)

            if deserialized.is_valid():
                try:
                    validated_data = deserialized.validated_data
                    parent_sheet = validated_data.pop('parent')
                    if parent_sheet.machine.pk != pk:
                        raise ValueError('machine with id: %s is not related to provided parent sheet' % pk)
                    child_sheet = parent_sheet.add_child_sheet(**validated_data)
                    serialized = serializers.ChildSheetSerializer(child_sheet)
                    return Response(serialized.data)
                except ValueError as ve:
                    return Response({'error': str(ve)})
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': "missing machine pk"})


class ParentSheetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ParentSheetSerializer
    queryset = ParentSheet.objects.all()


class ChildSheetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChildSheetListSerializer
    queryset = ChildSheet.objects.all()