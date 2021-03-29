from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from djmoney.contrib.django_rest_framework import MoneyField
from .models import Item, Stock, StockRequest, StockRequestGroup, \
    StockUnit, BaseStockUnit, AlternateStockUnit
from .properties.models import ItemProperties, Line, Tape, Paper, Panel, Liquid


class BaseStockUnitOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev']

class AlternateStockUnitOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev']


class BaseStockUnitSerializer(serializers.ModelSerializer):
    alternate_stock_units = AlternateStockUnitOptionSerializer(many=True)

    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev', 'alternate_stock_units']


class AlternateStockUnitSerializer(serializers.ModelSerializer):
    base_stock_units = BaseStockUnitOptionSerializer(many=True)

    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev', 'base_stock_units']


class BaseStockUnitRetrieveSerializer(BaseStockUnitSerializer):
    alternate_stock_units = AlternateStockUnitSerializer(many=True)


class AlternateStockUnitRetrieveSerializer(AlternateStockUnitSerializer):
    base_stock_units = BaseStockUnitSerializer(many=True)


class BaseStockUnitCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev', 'alternate_stock_units']

    def create(self, validated_data):
        alt_stock_units = validated_data.pop('alternate_stock_units')
        base_stock_unit = BaseStockUnit.objects.create(**validated_data)
        for alt_stock_unit in alt_stock_units:
            base_stock_unit.add_alt_stock_unit(alt_stock_unit.pk)
        return base_stock_unit
    
    def update(self, instance, validated_data):
        to_be_alts = validated_data.pop('alternate_stock_units')
        BaseStockUnit.objects.filter(pk=instance.pk).update(**validated_data)
        instance.update_alt_stock_units(to_be_alts)
        return instance


class AlternateStockUnitCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev', 'base_stock_units']

    def create(self, validated_data):
        base_stock_units = validated_data.pop('base_stock_units')
        alternate_stock_unit = AlternateStockUnit.objects.create(**validated_data)
        for base_stock_unit in base_stock_units:
            alternate_stock_unit.add_base_stock_unit(base_stock_unit.pk)
        return alternate_stock_unit
    
    def update(self, instance, validated_data):
        to_be_bases = validated_data.pop('base_stock_units')
        AlternateStockUnit.objects.filter(pk=instance.pk).update(**validated_data)
        instance.update_base_stock_units(to_be_bases)
        return instance


class ItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProperties
        fields = []


class LineSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Line
        fields = ['id', 'length_value', 'length_uom']

    def validate(self, data):
        errors = {}
        if data.get('length_value', None) is not None and data.get('length_uom', None) is None:
            errors['length_uom'] = 'Must provide value if length_value is populated'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class TapeSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Tape
        fields = ['id', 'length_value', 'length_uom', 'width_value', 'width_uom']

    def validate(self, data):
        errors = {}
        if data.get('length_value', None) is not None and data.get('length_uom', None) is None:
            errors['length_uom'] = 'Must provide value if length_value is populated'
        if data.get('width_value', None) is not None and data.get('width_uom', None) is None:
            errors['width_uom'] = 'Must provide value if width_value is populated'

        if errors:
            raise serializers.ValidationError(errors)

        return data


class PaperSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Paper
        fields = ['id', 'width_value', 'length_value', 'size_uom', 'gsm', 'finish']


class PanelSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Panel
        fields = ['id', 'width_value', 'length_value', 'size_uom', 'thickness_value', 'thickness_uom']

    def validate(self, data):
        if data.get('thickness_value', None) is not None and data.get('thickness_uom', None) is None:
            raise serializers.ValidationError(
                {'thickness_uom': 'Must provide value if thickness_value is populated'})
        return data


class LiquidSerializer(ItemPropertiesSerializer):
    class Meta:
        model = Liquid
        fields = ['id', 'volume_value', 'volume_uom']

    def validate(self, data):
        errors = {}
        if data.get('volume_value', None) is not None and data.get('volume_uom', None) is None:
            errors['volume_uom'] = 'Must provide value if volume_value is populated'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class ItemPropertiesPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ItemProperties: ItemPropertiesSerializer,
        Line: LineSerializer,
        Tape: TapeSerializer,
        Paper: PaperSerializer,
        Panel: PanelSerializer,
        Liquid: LiquidSerializer,
    }

    def to_resource_type(self, model_or_instance):
        return model_or_instance._meta.object_name.lower()


class StockSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=False, default_currency='PHP')
    price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True, default_currency='PHP')
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'brand_name', 'price', 'price_per_quantity', 
                    'unbounded', 'base_quantity', 'onhand_quantity',
                    'available_quantity', 'created_at']


class ItemSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=True, default_currency='PHP')
    base_uom = serializers.SlugRelatedField(slug_field='abbrev', read_only=True)
    alternate_uom = serializers.SlugRelatedField(slug_field='abbrev', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'full_name', 'type', 'price', 
            'available_quantity', 'available_quantity_formatted',
            'onhand_quantity', 'onhand_quantity_formatted',
            'base_uom', 'alternate_uom']


class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    override_price = MoneyField(max_digits=14, decimal_places=2)
    properties = ItemPropertiesPolymorphicSerializer(read_only=False)

    class Meta:
        model = Item
        fields = ['id', 'name', 'type', 'properties', 'override_price', 
                  'is_override_price', 'is_raw_material', 
                  'base_uom', 'alternate_uom']

    def update(self, instance, validated_data):
        validated_data.pop('type') #prevent changing type
        props = validated_data.pop('properties')
        Item.objects.filter(pk=instance.pk).update(**validated_data)
        if (props is not None):
            type_key = props.pop('resourcetype')
            clazz = ItemProperties.get_class(type_key)
            clazz.objects.filter(pk=instance.properties.pk).update(**props)
        return instance

    def create(self, validated_data):
        props = validated_data.pop('properties')
        item = Item.objects.create(**validated_data)
        if (props is not None):
            type_key = props.pop('resourcetype')
            clazz = ItemProperties.get_class(type_key)
            props = {k: v for k, v in props.items() if v is not None}
            itemprops = clazz.objects.create(item=item, **props)
        return item 


class ItemRetrieveSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    properties = ItemPropertiesPolymorphicSerializer(read_only=True)
    base_uom = BaseStockUnitSerializer()
    alternate_uom = AlternateStockUnitSerializer()

    class Meta:
        model = Item
        fields = ['id', 'name', 'full_name', 'type', 'properties', 'price', 
                  'override_price', 'is_override_price', 'is_raw_material',
                  'base_uom', 'alternate_uom']


class ItemStockRetrieveSerializer(serializers.ModelSerializer):
    latest_price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    average_price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    base_uom = BaseStockUnitSerializer()
    alternate_uom = AlternateStockUnitSerializer()

    class Meta:
        model = Item
        fields = ['id', 'latest_price_per_quantity', 'average_price_per_quantity',  
                  'available_quantity', 'available_quantity_formatted', 
                  'onhand_quantity', 'onhand_quantity_formatted', 
                   'base_uom', 'alternate_uom']


class StockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockUnit
        fields = ['id', 'quantity']


class StockRequestSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_unit = StockUnitSerializer(read_only=True)

    class Meta:
        model = StockRequest
        fields = ['id', 'stock', 'stock_unit', 'status', 'created', 'last_modified']


class StockRequestGroupSerializer(serializers.ModelSerializer):
    stock_requests = StockRequestSerializer(many=True, read_only=True)

    class Meta:
        model = StockRequestGroup
        fields = ['reason', 'stock_requests']