from inventory.models import Item, Stock, StockRequest, \
    StockRequestGroup, BaseStockUnit, AlternateStockUnit
from inventory.properties.models import ItemProperties
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.BaseStockUnitCreateUpdateSerializer
        elif self.action in ['retrieve']:
            return serializers.BaseStockUnitRetrieveSerializer
        else:
            return serializers.BaseStockUnitSerializer


class AlternateStockUnitViewSet(viewsets.ModelViewSet):
    queryset = AlternateStockUnit.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.AlternateStockUnitCreateUpdateSerializer
        elif self.action in ['retrieve']:
            return serializers.AlternateStockUnitRetrieveSerializer
        else:
            return serializers.AlternateStockUnitSerializer


class ItemPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ItemProperties.objects.all()

    def get_serializer_class(self):
        mapping = serializers.ItemPropertiesPolymorphicSerializer.model_serializer_mapping

        if self.action in ['retrieve', 'update', 'metadata']:    
            prop = self.get_object()    
            serializer = mapping[prop.__class__]
            return serializer
        else:
            return serializers.ItemPropertiesPolymorphicSerializer


class ItemPropertiesListCreateViewSet(ItemPropertiesViewSet):

    def get_serializer_class(self):
        mapping = serializers.ItemPropertiesPolymorphicSerializer.model_serializer_mapping
        item_type = self.request.GET.get('resourcetype', None)

        if (item_type and self.action in ['metadata']):
            clazz = ItemProperties.get_class(item_type)
            if (clazz is not None):
                serializer = mapping[clazz]
                return serializer
            else:
                return serializers.ItemPropertiesPolymorphicSerializer
        else:
            return serializers.ItemPropertiesPolymorphicSerializer


class ItemStockRetrieveViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemStockRetrieveSerializer


class ItemStockListViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StockSerializer

    def get_queryset(self):
        return Stock.objects.filter(item=self.kwargs['pk'])


class ItemDepositStockViewSet(viewsets.ViewSet):

    def create(self, request, pk=None):
        item = Item.objects.get(pk=pk)
        serializer = serializers.StockSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            brand_name = data.get('brand_name')
            base_quantity = data.get('base_quantity', 1)
            alt_quantity = int(request.data.get('alt_quantity', 1))
            price = data.get('price', None)
            unbounded = data.get('unbounded')
            
            deposited = item.deposit_stock(brand_name, base_quantity, price, alt_quantity, unbounded)
            serialized_deposited = serializers.StockSerializer(deposited, many=True)
            return Response(serialized_deposited.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemWithdrawStocksViewSet(viewsets.ViewSet):

    def create(self, request, pk=None):
        serializer = serializers.StockRequestGroupSerializer(data=request.data)

        if request.data and serializer.is_valid():
            stock_requests = []
            reason = request.data.get('reason', None)
            stocks = request.data.get('stock_requests', [])

            for entry in stocks:
                id = entry.get('id', None)
                quantity = int(entry.get('quantity', 0))
                if id is not None and quantity > 0:
                    try:
                        stock = Stock.objects.get(item=pk, pk=id)
                        stock_request = stock.request(quantity)
                        stock_requests.append(stock_request)
                    except Stock.DoesNotExist:
                        pass
            
            if len(stock_requests) > 0:
                stock_request_group = StockRequestGroup.objects.create(reason=reason)
                stock_request_group.stock_requests.set(stock_requests)
                serialized_request = serializers.StockRequestGroupSerializer(stock_request_group)
                return Response(serialized_request.data) 
            else:
                return Response({"data": "no available stocks"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
