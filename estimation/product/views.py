from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.product import serializers
from estimation.product.models import ProductEstimate
from estimation.template.models import ProductTemplate


class ProductEstimateView(mixins.ListModelMixin,
        mixins.CreateModelMixin, mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = ProductEstimate.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return serializers.ProductEstimateInputSerializer
        else:
            return serializers.ProductEstimateSerializer


class ProductEstimateCostView(mixins.RetrieveModelMixin, 
        viewsets.GenericViewSet):
    queryset = ProductEstimate.objects.all()
    serializer_class = serializers.ProductEstimateCostsSerializer