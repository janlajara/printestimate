from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from djmoney.contrib.django_rest_framework import MoneyField
from core.utils.measures import MeasurementSerializerField
from .models import Item, Stock, BaseStockUnit, AlternateStockUnit
from .properties.models import ItemProperties, Line, Tape, Paper, Panel, Liquid


class BaseStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 'plural_abbrev']


class AlternateStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 'plural_abbrev']


class ItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProperties
        fields = '__all__'


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ['length', 'length_value', 'length_uom']


class TapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tape
        fields = ['length', 'length_value', 'length_uom',
                  'width', 'width_value', 'width_uom']


class PaperSerializer(serializers.ModelSerializer):
    length = MeasurementSerializerField()
    width = MeasurementSerializerField()

    class Meta:
        model = Paper
        fields = ['length', 'width', 'length_value', 'width_value',
                  'size_uom', 'gsm', 'finish']


class PanelSerializer(serializers.ModelSerializer):
    thickness = MeasurementSerializerField()
    length = MeasurementSerializerField()
    width = MeasurementSerializerField()

    class Meta:
        model = Panel
        fields = ['length', 'width', 'length_value', 'width_value',
                  'size_uom', 'thickness', 'thickness_value', 'thickness_uom']


class LiquidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liquid
        fields = ['volume', 'volume_value', 'volume_uom']


class ItemPropertiesPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ItemProperties: ItemPropertiesSerializer,
        Line: LineSerializer,
        Tape: TapeSerializer,
        Paper: PaperSerializer,
        Panel: PanelSerializer,
        Liquid: LiquidSerializer,
    }


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class ItemListSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    base_uom = BaseStockUnitSerializer()
    alternate_uom = AlternateStockUnitSerializer()

    class Meta:
        model = Item
        fields = ['id', 'name', 'full_name', 'type', 'price', 'available_quantity',
                  'onhand_quantity', 'base_uom', 'alternate_uom']


class ItemCreateSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'full_name', 'type', 'price', 'available_quantity',
                  'onhand_quantity', 'base_uom', 'alternate_uom']


class ItemDetailSerializer(ItemCreateSerializer):
    override_price = MoneyField(max_digits=14, decimal_places=2)
    latest_price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    average_price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    properties = ItemPropertiesPolymorphicSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'full_name', 'type', 'properties', 'price',
                  'override_price', 'is_override_price', 'latest_price_per_quantity',
                  'average_price_per_quantity', 'is_raw_material', 'available_quantity',
                  'onhand_quantity', 'onhand_stocks', 'base_uom', 'alternate_uom']

    def create(self, validated_data):
        return Item.objects.create_item(**validated_data)
