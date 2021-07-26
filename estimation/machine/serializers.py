from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
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
    min_parent_sheet_length = serializers.SerializerMethodField()
    min_parent_sheet_width = serializers.SerializerMethodField()

    class Meta:
        model = SheetFedPressMachine
        fields = ['id', 'name', 'process_type', 
            'description', 'costing_measures', 
            'min_sheet_length', 'max_sheet_length', 
            'min_sheet_width', 'max_sheet_width', 'uom', 
            'length_range', 'width_range', 
            'min_parent_sheet_length', 'min_parent_sheet_width']
    
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

    def get_min_parent_sheet_length(self, obj):
        min_length_obj = obj.parent_sheets.order_by('length_value').first()
        return min_length_obj.length_value if min_length_obj else None

    def get_min_parent_sheet_width(self, obj):
        min_width_obj = obj.parent_sheets.order_by('width_value').first()
        return min_width_obj.width_value if min_width_obj else None

class MachinePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Machine: MachineSerializer,
        SheetFedPressMachine: SheetFedPressMachineSerializer
    }


class ChildSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildSheet
        fields = ['id', 'label', 'parent', 'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length']


class ChildSheetListSerializer(ChildSheetSerializer):
    size = serializers.SerializerMethodField()
    parent_size = serializers.SerializerMethodField()

    class Meta:
        model = ChildSheet
        fields = ['id', 'parent', 'parent_size', 'size', 'label', 
            'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length']


    def get_size(self, obj):
        return str(obj)

    def get_parent_size(self, obj):
        return str(obj.parent)


class ParentSheetSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    child_sheets = ChildSheetSerializer(read_only=True, many=True)

    class Meta:
        model = ParentSheet
        fields = ['id', 'size', 'label', 'width_value', 'length_value', 'size_uom',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
            'pack_width', 'pack_length', 'pack_size', 'child_sheets']

    def get_size(self, obj):
        return str(obj)


class ParentSheetLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentSheet
        fields = ['width_value', 'length_value', 'size_uom',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
            'pack_width', 'pack_length']


class ChildSheetLayoutSerializer(serializers.ModelSerializer):
    parent = ParentSheetLayoutSerializer()

    class Meta:
        model = ChildSheet
        fields = ['parent', 'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length']


class PackRectangle:
    def __init__(self, i=0, x=0, y=0, width=0, length=0, is_rotated=False):
        self.i = i
        self.x = x 
        self.y = y 
        self.width = width
        self.length = length
        self.is_rotated = is_rotated
    
    def area(self):
        return self.width * self.length


class PackRectangleSerializer(serializers.Serializer):
    i = serializers.IntegerField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    width = serializers.FloatField()
    length = serializers.FloatField()
    is_rotated = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.b = validated_data.get('i', instance.b)
        instance.x = validated_data.get('x', instance.x)
        instance.y = validated_data.get('y', instance.y)
        instance.width = validated_data.get('width', instance.width)
        instance.length = validated_data.get('length', instance.length)
        instance.is_rotated = validated_data.get('is_rotated', instance.is_rotated)
        return instance

    def create(self, validated_data):
        return PackRectangle(**validated_data)