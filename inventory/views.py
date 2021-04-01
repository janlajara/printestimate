from inventory.models import Item, Stock, StockRequest, \
    StockRequestGroup, StockMovement, BaseStockUnit, AlternateStockUnit
from inventory.properties.models import ItemProperties
from inventory.exceptions import InsufficientStock
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from inventory import serializers


# Create your views here.
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'type', 'stocks__brand_name']

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
            return serializers.BaseStockUnitRetrieveSerializer


class AlternateStockUnitViewSet(viewsets.ModelViewSet):
    queryset = AlternateStockUnit.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.AlternateStockUnitCreateUpdateSerializer
        elif self.action in ['retrieve']:
            return serializers.AlternateStockUnitRetrieveSerializer
        else:
            return serializers.BaseStockUnitRetrieveSerializer


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
    serializer_class = serializers.StockReadOnlySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        available_only = self.request.GET.get('available-only', False)
        all = Stock.objects.all()

        if pk is not None:
            all = all.filter(item=pk).all()
        if available_only and available_only.lower() == 'true':
            filtered = [stock for stock in all if stock.available_quantity > 0]
            return filtered
        else:
            return all


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
                    except InsufficientStock:
                        pass
            
            if len(stock_requests) > 0:
                stock_request_group = StockRequestGroup.objects.create(reason=reason)
                stock_request_group.stock_requests.set(stock_requests)
                serialized_request = serializers.StockRequestGroupSerializer(stock_request_group)
                return Response(serialized_request.data) 
            else:
                return Response({"detail": "no available stocks to withdraw"},
                    status=status.HTTP_409_CONFLICT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


class ItemStockRequestListViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StockRequestGroupSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        status = self.request.GET.get('status', 'Pending')
        all = StockRequestGroup.objects.all()
        status_map = {
            'Pending': [StockRequest.NEW, StockRequest.APPROVED],
            'Finished': [StockRequest.FULFILLED, StockRequest.CANCELLED]
        }
        if pk is not None:
            if status is not None and status_map[status] is not None:
                all = all.filter(stock_requests__stock__item__pk=pk,
                    stock_requests__status__in=status_map[status]).all()
            else:
                all = all.filter(stock_requests__stock__item__pk=pk).all()

        return all
    

class StockMovementSerializer(viewsets.ModelViewSet):
    serializer_class = serializers.StockMovementSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        all = StockMovement.objects.all()

        if pk is not None:
            all = all.filter(stock__item__pk=pk).all()

        return all
