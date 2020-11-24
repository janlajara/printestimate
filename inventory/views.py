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


class AlternateStockUnitViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AlternateStockUnitSerializer

    def get_queryset(self):
        queryset = AlternateStockUnit.objects.all()
        base_stock_unit_pk = self.request.GET.get('basestockunit', None)

        if base_stock_unit_pk is not None:
            queryset = AlternateStockUnit.objects.filter(base_stock_units__pk=base_stock_unit_pk)

        return queryset


class ItemPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ItemProperties.objects.all()
    serializer_class = serializers.ItemPropertiesPolymorphicSerializer
