from django.shortcuts import render
from rest_framework import viewsets
from core.utils.measures import Measure
from rest_framework.response import Response

# Create your views here.
class MeasureUnitsView(viewsets.ViewSet):
    def list(self, request):
        def map_values(obj):
            return {
                "measure": obj[0], 
                "measure_units": list(
                    map(lambda x: {
                        "value": x[0],
                        "display": x[1]
                    }, obj[1]))
            }
        mapping = [x for x in Measure.UNITS.items() if x[0] != Measure.TIME]
        mapped = list(map(map_values, mapping))
        return Response(mapped)