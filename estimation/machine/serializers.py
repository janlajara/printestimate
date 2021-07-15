from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from estimation.models import Machine, SheetFedPressMachine, ParentSheet, ChildSheet


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'name', 'type']


class SheetFedPressMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheetFedPressMachine
        fields = ['id', 'name', 'type', 'min_sheet_length', 'max_sheet_length',
            'min_sheet_width', 'max_sheet_width', 'uom']


class MachinePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Machine: MachineSerializer,
        SheetFedPressMachine: SheetFedPressMachineSerializer
    }


class ParentSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentSheet
        fields = ['id', 'width_value', 'length_value', 'size_uom',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
            'pack_width', 'pack_length']


class ChildSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentSheet
        fields = ['id', 'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length', 'usage', 'wastage']