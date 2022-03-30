from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from estimation.costaddons import serializers, models


class ConfigCostAddonViewSet(viewsets.ModelViewSet):
    queryset = models.ConfigCostAddon.objects.all()
    serializer_class = serializers.ConfigCostAddonSerializer


class TemplateCostAddonSetSerializerViewSet(viewsets.ModelViewSet):
    queryset = models.TemplateCostAddonSet.objects.all()
    serializer_class = serializers.TemplateCostAddonSetSerializer