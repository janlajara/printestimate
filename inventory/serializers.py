from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from djmoney.contrib.django_rest_framework import MoneyField
from .models import Item, Stock, BaseStockUnit, AlternateStockUnit
from .properties.models import ItemProperties, Line, Tape, Paper, Panel, Liquid


class BaseStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit
        fields = '__all__'


class AlternateStockUnitSerializer(serializers.ModelSerializer):
    #base_stock_units = BaseStockUnitSerializer(read_only=True, many=True)
    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable']


class ItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProperties
        fields = '__all__'


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = '__all__'


class TapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tape
        fields = '__all__'


class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = '__all__'


class PanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel
        fields = '__all__'


class LiquidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liquid
        fields = '__all__'


class PropertiesPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
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
    base_uom = BaseStockUnitSerializer(read_only=True)
    alternate_uom = AlternateStockUnitSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ['name', 'full_name', 'type', 'price', 'available_quantity',
                  'onhand_quantity', 'base_uom', 'alternate_uom']


class ItemDetailSerializer(ItemListSerialigzer):
    override_price = MoneyField(max_digits=14, decimal_places=2)
    latest_price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    average_price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    properties = ItemPropertiesSerializer()

    class Meta:
        model = Item
        fields = ['name', 'full_name', 'type', 'properties', 'price',
                  'override_price', 'is_override_price', 'latest_price_per_quantity',
                  'average_price_per_quantity', 'is_raw_material', 'available_quantity',
                  'onhand_quantity', 'onhand_stocks', 'base_uom', 'alternate_uom']
