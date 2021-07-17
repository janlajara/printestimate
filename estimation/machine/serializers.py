from rest_framework import serializers
#from rest_polymorphic.serializers import PolymorphicSerializer
from estimation.models import Machine, SheetFedPressMachine, ParentSheet, ChildSheet
from django.shortcuts import get_object_or_404
import inflect

_inflect = inflect.engine()

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'name', 'type', 'description']


class SheetFedPressMachineSerializer(serializers.ModelSerializer):
    length_range = serializers.SerializerMethodField()
    width_range = serializers.SerializerMethodField()

    class Meta:
        model = SheetFedPressMachine
        fields = ['id', 'name', 'process_type', 'description', 'min_sheet_length', 
            'max_sheet_length', 'min_sheet_width', 'max_sheet_width', 'uom', 
            'length_range', 'width_range']
    
    def validate(self, data):
        errors = {}

        if data['min_sheet_length'] > data['max_sheet_length']:
            errors["max_sheet_length"] = "value must be greater than 'min_sheet_length'"
        if data['min_sheet_width'] > data['max_sheet_width']:
            errors["max_sheet_width"] = "value must be greater than 'min_sheet_width'"

        if len(errors.items()) > 0:
            raise serializers.ValidationError(errors)

        return super().validate(data)

    def get_length_range(self, obj):
        return '%g - %g %s' % (obj.min_sheet_length, 
            obj.max_sheet_length, _inflect.plural(obj.uom))

    def get_width_range(self, obj):
        return '%g - %g %s' % (obj.min_sheet_width, 
            obj.max_sheet_width, _inflect.plural(obj.uom))


#class MachinePolymorphicSerializer(PolymorphicSerializer):
#    model_serializer_mapping = {
#        Machine: MachineSerializer,
#        SheetFedPressMachine: SheetFedPressMachineSerializer
#    }


class ChildSheetSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = ChildSheet
        fields = ['id', 'label', 'parent', 'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length']

    def get_label(self, obj):
        return str(obj)


class ChildSheetListSerializer(ChildSheetSerializer):
    parent = serializers.StringRelatedField()

    class Meta:
        model = ChildSheet
        fields = ['id', 'parent', 'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length', 'usage', 'wastage']


class ParentSheetSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    child_sheets = ChildSheetSerializer(read_only=True, many=True)

    class Meta:
        model = ParentSheet
        fields = ['id', 'size', 'label', 'width_value', 'length_value', 'size_uom',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
            'pack_width', 'pack_length', 'child_sheets']

    def get_size(self, obj):
        return str(obj)

    def get_label(self, obj):
        return obj.label if obj.label is not None else str(obj)