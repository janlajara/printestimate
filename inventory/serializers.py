from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from .models import Item, Stock, BaseStockUnit, AlternateStockUnit
from .properties.models import ItemProperties, Line, Tape, Paper, Panel, Liquid


class BaseStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit


class AlternateStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateStockUnit


class ItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProperties


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line


class TapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tape


class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper


class PanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel


class LiquidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liquid


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


class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'full_name', 'type', 'price', 'available_quantity',
                  'onhand_quantity', 'base_uom', 'alternate_uom']


class ItemDetailSerializer(serializers.ModelSerializer):
    properties = ItemPropertiesSerializer(read_only=True)
    #onhand_stocks = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['name', 'full_name', 'type', 'properties', 'price',
                  'override_price', 'is_override_price', 'latest_price_per_quantity',
                  'average_price_per_quantity', 'is_raw_material', 'available_quantity',
                  'onhand_quantity', 'onhand_stocks', 'base_uom', 'alternate_uom']
