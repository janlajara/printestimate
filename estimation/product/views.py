from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.product import serializers
from estimation.product.models import ProductEstimate
from estimation.template.models import ProductTemplate


class ProductEstimateView(mixins.CreateModelMixin, 
        mixins.ListModelMixin,mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = ProductEstimate.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return serializers.ProductEstimateInputSerializer
        else:
            return serializers.ProductEstimateListSerializer

    def retrieve(self, request, pk=None):
        if pk is not None:
            product_estimate = get_object_or_404(ProductEstimate, pk=pk)
            serializer = serializers.ProductEstimateRetrieveSerializer(product_estimate)
            return Response(serializer.data)
        else:
            return Response({'errors': 'estimate pk is not provided'},
                status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = serializers.ProductEstimateInputSerializer(data=request.data)

        if serializer.is_valid():
            request_data = serializer.validated_data
            product_estimate_id = request_data.get('id', None)
            product_template_id = request_data.get('product_template_id')
            order_quantities = request_data.get('order_quantities')
            product_template = get_object_or_404(ProductTemplate, pk=product_template_id)

            if product_estimate_id is not None:
                product_estimate = get_object_or_404(ProductEstimate, pk=product_estimate_id)
                product_estimate.set_estimate_quantities(order_quantities)
            else:
                product_estimate = ProductEstimate.objects.create_product_estimate(
                    product_template, order_quantities)

            serializer = serializers.ProductEstimateRetrieveSerializer(product_estimate)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)