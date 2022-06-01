from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from core.utils.shapes import Rectangle, RectangleLayoutMetaSerializer
from estimation.models import Machine, SheetFedPressMachine, RollFedPressMachine, \
    ParentSheet, ChildSheet
from estimation import serializers
import json


class MachineTypesViewSet(viewsets.ViewSet):
    def list(self, request):
        types = map(
            lambda x: { "value": x[0], "display": x[1]},
            Machine.TYPES)
        return Response(types)


class MachineViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.MachinePolymorphicSerializer

    def get_queryset(self):
        def __eval(a, b):
            return a == b if b is not None and b != '' else True

        query_params = self.request.query_params
        material_type = query_params.get('material_type', None)
        resourcetype = query_params.get('resourcetype', None)
        machines = Machine.objects.all()

        if material_type is not None or resourcetype is not None:
            machines = [x for x in machines if __eval(x.material_type, material_type)
                and __eval(x.__class__.__name__, resourcetype)]

        return machines


class SheetFedPressMachineViewSet(viewsets.ModelViewSet):
    queryset = SheetFedPressMachine.objects.all()
    serializer_class = serializers.SheetFedPressMachineSerializer

    def create(self, request):
        serializer = serializers.SheetFedPressMachineSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            machine = Machine.objects.create_machine(
                type=Machine.SHEET_FED_PRESS, **validated_data)
            serialized = serializers.SheetFedPressMachineSerializer(machine)
            return Response(serialized.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class RollFedPressMachineViewSet(viewsets.ModelViewSet):
    queryset = RollFedPressMachine.objects.all()
    serializer_class = serializers.RollFedPressMachineSerializer

    def create(self, request):
        serializer = serializers.RollFedPressMachineSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            machine = Machine.objects.create_machine(
                type=Machine.ROLL_FED_PRESS, **validated_data)
            serialized = serializers.RollFedPressMachineSerializer(machine)
            return Response(serialized.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


# For getting sheet layouts that do not involved any printers
class GetSheetLayoutsView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = []
    serializer_class = serializers.GetSheetLayoutSerializer

    def create(self, request):
        serializer = serializers.GetSheetLayoutSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            material_layout, item_layout, bleed, rotate = \
                    serializer.parse(validated_data)
            sheet_layout = ChildSheet.get_layout(item_layout, material_layout, 
                rotate)
            layouts = {}

            if sheet_layout is not None:
                serializer = serializers.SheetLayoutMetaSerializer(sheet_layout)
                layouts = serializer.data

            return Response({
                    "machine_type": None,
                    "layouts": [layouts]
                })
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SheetFedPressMachineGetSheetLayoutsView(mixins.CreateModelMixin,  
        viewsets.GenericViewSet):
    queryset = []
    serializer_class = serializers.GetSheetLayoutSerializer

    def create(self, request, pk):
        if pk is not None:
            press_machine = get_object_or_404(SheetFedPressMachine, pk=pk)
            serializer = serializers.GetSheetLayoutSerializer(data=request.data)
            
            if serializer.is_valid():
                validated_data = serializer.validated_data
                material_layout, item_layout, bleed, rotate = \
                    serializer.parse(validated_data)
                sheet_layouts, layout_type = press_machine.get_sheet_layouts(item_layout, 
                    material_layout, rotate)

                layouts = {}
                if sheet_layouts is not None:
                    serializer = serializers.SheetLayoutMetaSerializer(sheet_layouts, many=True)
                    layouts = serializer.data

                return Response({
                    "machine_type": layout_type,
                    "layouts": layouts
                })
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "missing machine pk"}, status.HTTP_400_BAD_REQUEST)


class RollFedPressMachineGetSheetLayoutsView(mixins.CreateModelMixin,  
        viewsets.GenericViewSet):
    queryset = []
    serializer_class = serializers.GetRollFedMachineSheetLayoutSerializer

    def create(self, request, pk):
        if pk is not None:
            press_machine = get_object_or_404(RollFedPressMachine, pk=pk)
            serializer = serializers.GetRollFedMachineSheetLayoutSerializer(data=request.data)
            
            if serializer.is_valid():
                validated_data = serializer.validated_data
                (material_layout, item_layout, order_quantity,
                    spoilage_rate, apply_breakpoint) = serializer.parse(validated_data)
                sheet_layouts, layout_type = press_machine.get_sheet_layouts(item_layout, 
                    material_layout, False, order_quantity=order_quantity, 
                    spoilage_rate=spoilage_rate, apply_breakpoint=apply_breakpoint)

                layouts = {}
                if sheet_layouts is not None:
                    serializer = serializers.SheetLayoutMetaSerializer(sheet_layouts, many=True)
                    layouts = serializer.data

                return Response({
                    "machine_type": layout_type,
                    "layouts": layouts
                })
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "missing machine pk"}, status.HTTP_400_BAD_REQUEST)