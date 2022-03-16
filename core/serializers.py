from rest_framework import serializers
from core.utils.measures import Measure, CostingMeasure


class UnitSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=Measure.PRIMARY_UNITS)
    display_name = serializers.CharField(required=False)


class CostingMeasureSerializer(serializers.Serializer):
    name = serializers.ChoiceField(choices=CostingMeasure.TYPES)
    units = UnitSerializer(many=True, required=False)