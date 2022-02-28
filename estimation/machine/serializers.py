from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from inventory.properties.models import Paper
from core.utils.shapes import Rectangle, RectangleLayoutSerializer, RectangleLayoutMetaSerializer
from estimation.models import Machine, SheetFedPressMachine, ParentSheet, ChildSheet
from django.shortcuts import get_object_or_404
import inflect

_inflect = inflect.engine()

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'name', 'type', 'material_type', 'description']


class SheetFedPressMachineSerializer(serializers.ModelSerializer):
    length_range = serializers.SerializerMethodField()
    width_range = serializers.SerializerMethodField()
    min_parent_sheet_length = serializers.SerializerMethodField()
    min_parent_sheet_width = serializers.SerializerMethodField()

    class Meta:
        model = SheetFedPressMachine
        fields = ['id', 'name', 'process_type', 'material_type',
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


class ParentSheetSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentSheet
        fields = ['width_value', 'length_value', 'size_uom',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
            'pack_width', 'pack_length']


class ChildSheetSimpleSerializer(serializers.ModelSerializer):
    parent = ParentSheetSimpleSerializer()

    class Meta:
        model = ChildSheet
        fields = ['parent', 'width_value', 'length_value', 'size_uom',
            'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
            'pack_width', 'pack_length']


class ParentSheetLayoutSerializer(RectangleLayoutSerializer):
    padding_top = serializers.FloatField()
    padding_right = serializers.FloatField()
    padding_bottom = serializers.FloatField()
    padding_left = serializers.FloatField()

    def create(self, validated_data):
        return ParentSheet.Layout(**validated_Data)

    def update(self, instance, validated_data):
        instance = super().update(self, instance, validated_data)
        instance.padding_top = validated_data.get('padding_top', instance.padding_top)
        instance.padding_right = validated_data.get('padding_right', instance.padding_right)
        instance.padding_bottom = validated_data.get('padding_bottom', instance.padding_bottom)
        instance.padding_left = validated_data.get('padding_left', instance.padding_left)
        return instance


class ChildSheetLayoutSerializer(RectangleLayoutSerializer):
    margin_top = serializers.FloatField(default=0)
    margin_right = serializers.FloatField(default=0)
    margin_bottom = serializers.FloatField(default=0)
    margin_left = serializers.FloatField(default=0)

    def create(self, validated_data):
        return ChildSheet.Layout(**validated_data)

    def update(self, instance, validated_data):
        instance = super().update(self, instance, validated_data)
        instance.margin_top = validated_data.get('margin_top', instance.margin_top)
        instance.margin_right = validated_data.get('margin_right', instance.margin_right)
        instance.margin_bottom = validated_data.get('margin_bottom', instance.margin_bottom)
        instance.margin_left = validated_data.get('margin_left', instance.margin_left)
        return instance


class PolymorphicSheetLayoutSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Rectangle.Layout: RectangleLayoutSerializer,
        Paper.Layout:  RectangleLayoutSerializer,
        ChildSheet.Layout: ChildSheetLayoutSerializer,
        ParentSheet.Layout: ParentSheetLayoutSerializer
    }

    def to_resource_type(self, model_or_instance):
        return type(model_or_instance).__qualname__

    def _get_serializer_from_model_or_instance(self, model_or_instance):
        resourcetype = type(model_or_instance).__qualname__

        for klazz, serializer in self.model_serializer_mapping.items():
            if klazz.__qualname__ == resourcetype:
                return serializer
        
        raise KeyError(
            '`{clz}.model_serializer_mapping` is missing '
            'a corresponding serializer for `{model}` model'.format(
                clz=self.__class__.__name__,
                model=type(model_or_instance).__qualname__))


class SheetLayoutMetaSerializer(RectangleLayoutMetaSerializer):
    bin = PolymorphicSheetLayoutSerializer()
    rect = PolymorphicSheetLayoutSerializer()
    layouts = PolymorphicSheetLayoutSerializer(many=True)


class GetSheetLayoutSerializer(serializers.Serializer):
    material_layout = ChildSheetLayoutSerializer()
    item_layout = RectangleLayoutSerializer()
    bleed = serializers.BooleanField(default=False)
    rotate = serializers.BooleanField(default=False)

    def create(self, validated_data):
        material_layout_data = validated_data.get('material_layout')
        material_layout = ChildSheet.Layout(**material_layout_data)

        item_layout_data = validated_data.get('item_layout')
        item_layout = Rectangle.Layout(**item_layout_data)

        bleed = validated_data.get('bleed', False)
        rotate = validated_data.get('rotate', False)

        return material_layout, item_layout, bleed, rotate