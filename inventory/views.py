from inventory.models import Item, BaseStockUnit, AlternateStockUnit
from inventory.properties.models import ItemProperties
from rest_framework import viewsets
from inventory import serializers


# Create your views here.
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.ItemCreateUpdateSerializer
        elif self.action in ['retrieve']:
            return serializers.ItemRetrieveSerializer
        else:
            return serializers.ItemSerializer


class BaseStockUnitViewSet(viewsets.ModelViewSet):
    queryset = BaseStockUnit.objects.all()
    serializer_class = serializers.BaseStockUnitSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.BaseStockUnitSerializer
        elif self.action in ['retrieve']:
            return serializers.BaseStockUnitDetailedSerializer
        else:
            return serializers.BaseStockUnitSerializer


class AlternateStockUnitViewSet(viewsets.ModelViewSet):
    queryset = AlternateStockUnit.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.AlternateStockUnitSerializer
        elif self.action in ['retrieve']:
            return serializers.AlternateStockUnitSerializer
        else:
            return serializers.AlternateStockUnitSerializer


class ItemPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ItemProperties.objects.all()

    def get_serializer_class(self):
        prop = self.get_object()
        mapping = serializers.ItemPropertiesPolymorphicSerializer.model_serializer_mapping
        serializer = mapping[prop.__class__]
        if self.action in ['metadata', 'update'] and serializer is not None:
            return serializer
        else:
            return serializers.ItemPropertiesPolymorphicSerializer
