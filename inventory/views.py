from inventory.models import Item
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from inventory import serializers


# Create your views here.
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return serializers.ItemDetailSerializer
        else:
            return serializers.ItemListSerializer

