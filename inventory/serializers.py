from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from djmoney.contrib.django_rest_framework import MoneyField
from .models import Item, Stock, StockRequest, ItemRequestGroup, \
    ItemRequest, StockUnit, BaseStockUnit, AlternateStockUnit, StockMovement
from .properties.models import ItemProperties, LineProperties, TapeProperties, \
    PaperProperties, PanelProperties, LiquidProperties


class BaseStockUnitOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev']

class AlternateStockUnitOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev']


class BaseStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev']


class AlternateStockUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev']


class BaseStockUnitRetrieveSerializer(BaseStockUnitSerializer):
    alternate_stock_units = AlternateStockUnitSerializer(many=True)

    class Meta:
        model = BaseStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev', 'alternate_stock_units']


class AlternateStockUnitRetrieveSerializer(AlternateStockUnitSerializer):
    base_stock_units = BaseStockUnitSerializer(many=True)

    class Meta:
        model = AlternateStockUnit
        fields = ['id', 'name', 'abbrev', 'is_editable', 'plural_name', 
            'plural_abbrev', 'base_stock_units']


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
        model = LineProperties
        fields = ['properties_id', 'length_value', 'length_uom']

    def validate(self, data):
        errors = {}
        if data.get('length_value', None) is not None and data.get('length_uom', None) is None:
            errors['length_uom'] = 'Must provide value if length_value is populated'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class TapeSerializer(ItemPropertiesSerializer):
    class Meta:
        model = TapeProperties
        fields = ['properties_id', 'length_value', 'length_uom', 'width_value', 'width_uom']

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
        model = PaperProperties
        fields = ['properties_id', 'width_value', 'length_value', 'size_uom', 'gsm', 'finish']


class PanelSerializer(ItemPropertiesSerializer):
    class Meta:
        model = PanelProperties
        fields = ['properties_id', 'width_value', 'length_value', 'size_uom', 'thickness_value', 'thickness_uom']

    def validate(self, data):
        if data.get('thickness_value', None) is not None and data.get('thickness_uom', None) is None:
            raise serializers.ValidationError(
                {'thickness_uom': 'Must provide value if thickness_value is populated'})
        return data


class LiquidSerializer(ItemPropertiesSerializer):
    class Meta:
        model = LiquidProperties
        fields = ['properties_id', 'volume_value', 'volume_uom']

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
        LineProperties: LineSerializer,
        TapeProperties: TapeSerializer,
        PaperProperties: PaperSerializer,
        PanelProperties: PanelSerializer,
        LiquidProperties: LiquidSerializer,
    }

    def to_resource_type(self, model_or_instance):
        mapping = {
            LineProperties.__name__: Item.LINE,
            TapeProperties.__name__: Item.TAPE,
            PaperProperties.__name__: Item.PAPER,
            PanelProperties.__name__: Item.PANEL,
            LiquidProperties.__name__: Item.LIQUID,
            ItemProperties.__name__: Item.OTHER
        }
        object_name = model_or_instance._meta.object_name
        resource_type = mapping.get(object_name, 'other')
        return resource_type


class StockSerializer(serializers.ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, read_only=False, default_currency='PHP')

    class Meta:
        model = Stock
        fields = ['id', 'brand_name', 'price', 'unbounded', 'base_quantity']


class StockReadOnlySerializer(StockSerializer):
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='PHP')
    price_per_quantity = MoneyField(max_digits=14, decimal_places=2, read_only=True, default_currency='PHP')
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    base_uom = serializers.SerializerMethodField()
    alternate_uom = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ['id', 'brand_name', 'price', 'price_per_quantity', 
                    'unbounded', 'base_uom', 'alternate_uom', 
                    'base_quantity', 'base_quantity_formatted',
                    'onhand_quantity', 'onhand_quantity_formatted',
                    'available_quantity', 'available_quantity_formatted',
                    'created_at']
    
    def get_base_uom(self, obj):
        serialized = BaseStockUnitSerializer(obj.item.base_uom)
        return serialized.data

    def get_alternate_uom(self, obj):
        serialized = AlternateStockUnitSerializer(obj.item.alternate_uom)
        return serialized.data


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
        itemprops = None
        if (props is not None):
            type_key = props.pop('resourcetype')
            clazz = ItemProperties.get_class(type_key)
            props = {k: v for k, v in props.items() if v is not None}
            itemprops = clazz.objects.create(**props)
        item = Item.objects.create(properties=itemprops, **validated_data)
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
        fields = ['id', 'quantity', 'quantity_formatted']


class StockRequestSerializer(serializers.ModelSerializer):
    stock_name = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    quantity_formatted = serializers.SerializerMethodField()

    class Meta:
        model = StockRequest
        fields = ['id', 'stock', 'stock_name', 'is_fulfilled', 
            'quantity', 'quantity_formatted']

    def get_stock_name(self, obj):
        return obj.stock.brand_name
    
    def get_quantity(self, obj):
        return obj.stock_unit.quantity
    
    def get_quantity_formatted(self, obj):
        return obj.stock_unit.quantity_formatted


class ItemRequestListSerializer(serializers.ModelSerializer):
    item_id = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    item_base_uom = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display') 

    class Meta:
        model = ItemRequest
        fields = ['id', 'item_id', 'item_name', 'item_base_uom', 'status', 
            'quantity_needed', 'quantity_needed_formatted', 
            'quantity_stocked', 'quantity_stocked_formatted',
            'is_fully_allocated', 'allocation_rate',
            'missing_allocation', 'missing_allocation_formatted', 
            'created']

    def get_item_id(self, obj):
        return obj.item.id

    def get_item_name(self, obj):
        return '%s' % obj.item

    def get_item_base_uom(self, obj):
        serialized = BaseStockUnitSerializer(obj.item.base_uom)
        return serialized.data


class ItemRequestDetailSerializer(ItemRequestListSerializer):
    status = serializers.CharField(read_only=True, source='get_status_display')
    status_choices = serializers.SerializerMethodField()
    stock_requests = StockRequestSerializer(many=True, read_only=True)
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = ItemRequest
        fields = ['id', 'item_id', 'item_name', 'item_base_uom', 
            'status', 'status_choices', 
            'quantity_needed', 'quantity_needed_formatted', 
            'quantity_stocked', 'quantity_stocked_formatted',
            'is_fully_allocated', 'allocation_rate',
            'missing_allocation', 'missing_allocation_formatted', 
            'stock_requests', 'created']

    def get_status_choices(self, obj):
        choices = []
        for choice in obj.status_choices:
            entry = {
                "value": choice[0],
                "label": choice[1]
            }
            choices.append(entry)
        return choices


class ItemRequestGroupSerializer(serializers.ModelSerializer):
    item_requests = ItemRequestDetailSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = ItemRequestGroup
        fields = ['id', 'status', 'finished', 'progress_rate', 
            'reason', 'item_requests', 'created_at']


class ItemRequestGroupListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = ItemRequestGroup
        fields = ['id', 'status', 'finished', 'progress_rate', 'reason', 
            'created_at']


class StockMovementSerializer(serializers.ModelSerializer):
    stock = StockReadOnlySerializer(read_only=True)
    stock_unit = StockUnitSerializer(read_only=True)
    action = serializers.CharField(source='get_action_display') 
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'stock', 'stock_unit', 'action', 'created']
