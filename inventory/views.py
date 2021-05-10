from inventory.models import Item, Stock, StockRequest, ItemRequest, \
    ItemRequestGroup, StockMovement, BaseStockUnit, AlternateStockUnit
from inventory.properties.models import ItemProperties
from inventory.exceptions import InsufficientStock
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
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
            return serializers.AlternateStockUnitRetrieveSerializer


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
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'brand_name']

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        available_only = self.request.GET.get('available-only', False)
        all = Stock.objects.all()

        if pk is not None:
            all = all.filter(item=pk).all()
        if available_only and available_only.lower() == 'true':
            filtered_ids = [stock.id for stock in all if stock.available_quantity > 0]
            all = all.filter(pk__in=filtered_ids)
       
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
        item = Item.objects.get(pk=pk)
        stock_requests = []
        item_request_id = request.data.get('item_request_id', None)
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
            if item_request_id is not None:
                item_request = get_object_or_404(ItemRequest, pk=item_request_id)
                item_request.allocate_stocks(stock_requests)
                item_request_group = ItemRequestGroup.objects.get(
                    item_requests__pk=item_request.pk)
                    
                serialized = serializers.ItemRequestGroupSerializer(item_request_group)
                return Response(serialized.data) 
            else:
                total_quantity = sum(stock_request.stock_unit.quantity 
                    for stock_request in stock_requests)
                item_request = item.request(total_quantity)
                item_request.allocate_stocks(stock_requests)

                item_request_group = ItemRequestGroup.objects.create(reason=reason)
                item_request_group.item_requests.add(item_request)

                serialized = serializers.ItemRequestGroupSerializer(item_request_group)
                return Response(serialized.data) 
        else:
            return Response({"detail": "no available stocks to withdraw"},
                status=status.HTTP_409_CONFLICT) 


class ItemRequestGroupItemDetailViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ItemRequestGroupSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        status = self.request.GET.get('status', 'Open')
        all = ItemRequestGroup.objects.all()
        status_map = {
            'open': [ItemRequest.DRAFT, ItemRequest.FOR_APPROVAL, ItemRequest.APPROVED],
            'closed': [ItemRequest.FULFILLED, ItemRequest.CANCELLED]
        }
        if pk is not None:
            if status is not None and status_map.get(status.lower()) is not None:
                all = all.filter(item_requests__item__pk=pk,
                    item_requests__status__in=status_map[status.lower()]).distinct()
            else:
                all = all.filter(item_requests__item__pk=pk).all()

        return all


class ItemRequestGroupViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id', 'reason'] 

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        status = self.request.GET.get('status', 'Open')
        all = ItemRequestGroup.objects.all()
        status_map = {
            'open': [ItemRequest.DRAFT, ItemRequest.FOR_APPROVAL, ItemRequest.APPROVED],
            'closed': [ItemRequest.FULFILLED, ItemRequest.CANCELLED]
        }
        if pk is not None:
            all = all.filter(pk=pk)
        elif status is not None and status_map.get(status.lower()) is not None:
            all = all.filter(item_requests__status__in=status_map[status.lower()]).distinct()
        return all

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.ItemRequestGroupListSerializer
        elif self.action in ['retrieve']:
            return serializers.ItemRequestGroupSerializer
        else:
            return serializers.ItemRequestGroupSerializer    


class ItemRequestsGroupAddItemRequestViewSet(viewsets.ViewSet):
    def update(self, request, pk=None):
        data = request.data

        if pk is not None:
            item_request_group = get_object_or_404(ItemRequestGroup, pk=pk)
            quantity = data.get('quantity', None)
            item_id = data.get('item_id', None)

            if quantity is not None and item_id is not None:
                item = get_object_or_404(Item, pk=item_id)
                item_request = item_request_group.add_item_request(item.pk, quantity)
                serialized = serializers.ItemRequestGroupSerializer(item_request_group)
                return Response(serialized.data)
            else:
                return Response(
                    {"detail": "Missing properties 'quantity' and/or 'item_id'."},
                        status=status.HTTP_400_BAD_REQUEST)
        return Response(
                    {"detail": "Missing query parameter 'pk'."},
                        status=status.HTTP_400_BAD_REQUEST)
            

class ItemRequestViewSet(viewsets.ModelViewSet):
    queryset = ItemRequest.objects.all()
    serializer_class = serializers.ItemRequestDetailSerializer


class ItemRequestUpdateStatusViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        data = request.data

        if pk is not None:
            item_request = ItemRequest.objects.get(pk=pk)
            request_status = data.get('status', None)
            comments = data.get('comments', None)

            if item_request is not None and request_status is not None:
                if request_status == ItemRequest.DRAFT:
                    item_request.draft(comments)
                elif request_status == ItemRequest.FOR_APPROVAL:
                    item_request.for_approval(comments)
                elif request_status == ItemRequest.APPROVED:
                    item_request.approve(comments)
                elif request_status == ItemRequest.FULFILLED:
                    item_request.fulfill(comments)
                elif request_status == ItemRequest.PARTIALLY_FULFILLED:
                    item_request.partially_fulfill(comments)
                elif request_status == ItemRequest.DISAPPROVED:
                    item_request.disapprove(comments)
                elif request_status == ItemRequest.CANCELLED:
                    item_request.cancel(comments)
                serialized = serializers.ItemRequestDetailSerializer(item_request)
                return Response(serialized.data)
            else:
                return Response(
                    {"error": "Stock request could not be found"}, 
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Missing stock request id"}, 
                status=status.HTTP_400_BAD_REQUEST)


class StockRequestViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StockRequestSerializer
    queryset = StockRequest.objects.all()


class StockMovementViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StockMovementSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        all = StockMovement.objects.all()

        if pk is not None:
            all = all.filter(stock__item__pk=pk).all()

        return all
