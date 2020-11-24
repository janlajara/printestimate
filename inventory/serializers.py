from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from djmoney.contrib.django_rest_framework import MoneyField
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
        fields = []


class LineSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Line
        fields = ['id', 'length_value', 'length_uom']


class TapeSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Tape
        fields = ['id', 'length_value', 'length_uom', 'width_value', 'width_uom']


class PaperSerializer(ItemPropertiesSerializer):

    class Meta:
        model = Paper
        fields = ['id', 'length_value', 'width_value', 'size_uom', 'gsm', 'finish']


class PanelSerializer(ItemPropertiesSerializer):

    class Meta:
        model = Panel
        fields = ['id', 'length_value', 'width_value', 'size_uom', 'thickness_value', 'thickness_uom']


class LiquidSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Liquid
        fields = ['id', 'volume_value', 'volume_uom']


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


class ItemSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    base_uom = serializers.SlugRelatedField(slug_field='abbrev', read_only=True)
    alternate_uom = serializers.SlugRelatedField(slug_field='abbrev', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'full_name', 'type', 'price', 'available_quantity',
                  'onhand_quantity', 'base_uom', 'alternate_uom']


class ItemCreateUpdateSerializer(ItemSerializer):
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


class ItemRetrieveSerializer(ItemCreateUpdateSerializer):
    base_uom = BaseStockUnitSerializer()
    alternate_uom = AlternateStockUnitSerializer()
