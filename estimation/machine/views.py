from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
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
            return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)


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
                    return Response({'error': str(ve)}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "missing machine pk"}, status.HTTP_400_BAD_REQUEST)


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
                    if parent_sheet.machine.pk != int(pk):
                        raise ValueError('machine with id: %s is not related to provided parent sheet' % pk)
                    child_sheet = parent_sheet.add_child_sheet(**validated_data)
                    serialized = serializers.ChildSheetSerializer(child_sheet)
                    return Response(serialized.data)
                except ValueError as ve:
                    return Response({'error': str(ve)}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "missing machine pk"}, status.HTTP_400_BAD_REQUEST)


class ParentSheetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ParentSheetSerializer
    queryset = ParentSheet.objects.all()


class ChildSheetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChildSheetListSerializer
    queryset = ChildSheet.objects.all()


class ChildSheetLayoutView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ChildSheetLayoutSerializer

    def get_layouts(self, child_sheet, rotate):
        parent = child_sheet.get('parent')
        parent_width = parent.get('width_value')
        parent_length = parent.get('length_value')
        parent_uom = parent.get('size_uom')
        parent_padding_top = parent.get('padding_top')
        parent_padding_right = parent.get('padding_right')
        parent_padding_bottom = parent.get('padding_bottom')
        parent_padding_left = parent.get('padding_left')
        parent_sheet = serializers.ParentSheetSerializer(parent)

        child_width = child_sheet.get('width_value')
        child_length = child_sheet.get('length_value')
        child_uom = child_sheet.get('size_uom')
        child_margin_top = child_sheet.get('margin_top')
        child_margin_right = child_sheet.get('margin_right')
        child_margin_bottom = child_sheet.get('margin_bottom')
        child_margin_left = child_sheet.get('margin_left')

        if parent_width == 0 + parent_length == 0 or child_width + child_length == 0:
            raise ValueError('size must be greater than zero')

        packer, count, usage, wastage = ChildSheet.get_layout(
            parent_width, parent_length, parent_uom,
            parent_padding_top, parent_padding_bottom,
            parent_padding_right, parent_padding_left,
            child_width, child_length, child_uom,
            child_margin_top, child_margin_bottom,
            child_margin_right, child_margin_left, 
            rotate)
        layouts = []
        
        for key, rect in enumerate(packer.rect_list()):
            x, y, width, length, rid = rect
            is_rotated = rotate and not(width == child_width and length == child_length)
            layout = serializers.PackRectangle(key + 1, x, y, width, length, is_rotated)
            layouts.append(layout) 

        return layouts, count, usage, wastage

    def create(self, request):
        deserialized = serializers.ChildSheetLayoutSerializer(data=request.data)

        if deserialized.is_valid():
            try:
                child_sheet = deserialized.validated_data
                rotate_layouts, rotate_count, rotate_usage, rotate_wastage = self.get_layouts(child_sheet, True)
                no_rotate_layouts, no_rotate_count, no_rotate_usage, no_rotate_wastage = self.get_layouts(child_sheet, False)

                rotate_serialized = serializers.PackRectangleSerializer(rotate_layouts, many=True)
                no_rotate_serialized = serializers.PackRectangleSerializer(no_rotate_layouts, many=True)

                return Response({
                    "allow_rotate": {
                        "count": rotate_count,
                        "usage": rotate_usage,
                        "wastage": rotate_wastage,
                        "rects": rotate_serialized.data,
                    },
                    "no_rotate": {
                        "count": no_rotate_count,
                        "usage": no_rotate_usage,
                        "wastage": no_rotate_wastage,
                        "rects": no_rotate_serialized.data
                    }
                })
            except ValueError as ve:
                return Response({'error': str(ve)}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response(deserialized.errors, status.HTTP_400_BAD_REQUEST)

        